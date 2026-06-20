import json
from pathlib import Path

from app.core.exceptions import InvalidFileError, ResourceNotFoundError
from app.models.processing_log_model import ProcessingLog
from app.models.report_model import Report
from app.models.user_model import User
from app.repositories.report_repository import ReportRepository
from app.schemas.email_schema import EmailSendResponse, ReportEmailRequest
from app.schemas.report_schema import ReportCreate, ReportGenerationResponse
from app.services.email_service import EmailService
from app.services.report_file_service import ReportFileService


class ReportService:
    """Coordina generación, persistencia, descarga y correo de reportes."""

    def __init__(
        self,
        repository: ReportRepository,
        files: ReportFileService | None = None,
        email: EmailService | None = None,
    ) -> None:
        self.repository = repository
        self.files = files or ReportFileService()
        self.email = email or EmailService()

    async def list(self, page: int, page_size: int) -> tuple[list[Report], int]:
        """Lista reportes usando paginación."""
        return await self.repository.list((page - 1) * page_size, page_size)

    async def get(self, report_id: int) -> Report:
        """Obtiene un reporte o informa que no existe."""
        report = await self.repository.get_by_id(report_id)
        if report is None:
            raise ResourceNotFoundError("Reporte no encontrado.")
        return report

    async def generate(
        self,
        data: ReportCreate,
        user: User,
    ) -> ReportGenerationResponse:
        """Genera el archivo, lo registra e intenta enviarlo automáticamente."""
        invoices = await self.repository.get_invoices(
            data.date_from,
            data.date_to,
            data.provider_id,
            data.status,
        )
        path = self.files.generate(invoices, data.file_format)
        report = Report(
            report_type="invoice_administrative",
            file_format=data.file_format.value,
            file_path=str(path),
            filters_json=json.dumps(
                data.model_dump(mode="json"),
                ensure_ascii=False,
            ),
            generated_by_id=user.id,
        )
        log = ProcessingLog(
            user_id=user.id,
            action="report_generated",
            status="success",
            result=(
                f"Reporte {data.file_format.value.upper()} generado con "
                f"{len(invoices)} factura(s)."
            ),
        )
        try:
            report = await self.repository.create_with_log(report, log)
        except Exception:
            # Si la transacción falla, elimina el reporte huérfano del disco.
            self.files.delete(path)
            raise

        recipient = self.email.automatic_recipient(user.email)
        delivery_mode = None
        email_error = None
        try:
            delivery_mode = self.email.send_report(
                report,
                path,
                ReportEmailRequest(
                    recipient=recipient,
                    subject="Reporte automático de facturas - SmartInvoice",
                    message=(
                        "SmartInvoice generó automáticamente el reporte "
                        f"#{report.id} con {len(invoices)} factura(s). "
                        "El archivo se encuentra adjunto."
                    ),
                ),
            )
            await self.repository.create_log(
                ProcessingLog(
                    user_id=user.id,
                    action="report_emailed",
                    status="success",
                    result=(
                        f"Reporte {report.id} enviado automáticamente a "
                        f"{recipient} mediante {delivery_mode}."
                    ),
                )
            )
        except Exception as exc:
            # El reporte se conserva aunque falle el correo; el fallo queda auditado.
            email_error = str(exc)
            await self.repository.create_log(
                ProcessingLog(
                    user_id=user.id,
                    action="report_email_error",
                    status="error",
                    result=(
                        f"Falló el envío automático del reporte {report.id} "
                        f"a {recipient}."
                    ),
                    error_detail=email_error,
                )
            )

        return ReportGenerationResponse(
            report=report,
            invoice_count=len(invoices),
            automatic_email_sent=delivery_mode is not None,
            automatic_email_recipient=recipient,
            automatic_email_delivery_mode=delivery_mode,
            automatic_email_error=email_error,
        )

    async def get_download(self, report_id: int) -> tuple[Report, Path]:
        """Comprueba que el archivo registrado exista y sea descargable."""
        report = await self.get(report_id)
        try:
            return report, self.files.get_existing_path(report.file_path)
        except InvalidFileError:
            raise

    async def send_email(
        self,
        report_id: int,
        data: ReportEmailRequest,
        user: User,
    ) -> EmailSendResponse:
        """Reenvía un reporte y registra tanto éxito como error."""
        report, path = await self.get_download(report_id)
        try:
            delivery_mode = self.email.send_report(report, path, data)
            await self.repository.create_log(
                ProcessingLog(
                    user_id=user.id,
                    action="report_emailed",
                    status="success",
                    result=(
                        f"Reporte {report.id} enviado a {data.recipient} "
                        f"mediante {delivery_mode}."
                    ),
                )
            )
            return EmailSendResponse(
                sent=True,
                delivery_mode=delivery_mode,
                recipient=data.recipient,
                report_id=report.id,
            )
        except Exception as exc:
            # Registra el detalle técnico antes de propagar el error al controlador.
            await self.repository.create_log(
                ProcessingLog(
                    user_id=user.id,
                    action="report_email_error",
                    status="error",
                    result=f"Falló el envío del reporte {report.id}.",
                    error_detail=str(exc),
                )
            )
            raise
