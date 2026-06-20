from fastapi import HTTPException, status

from app.core.exceptions import BusinessRuleError, ResourceNotFoundError
from app.models.invoice_model import InvoiceStatus
from app.models.processing_log_model import ProcessingLog
from app.models.user_model import User
from app.repositories.invoice_repository import InvoiceRepository
from app.schemas.rpa_schema import RpaExecutionResponse
from app.services.rpa_service import RpaService


class RpaController:
    def __init__(
        self,
        invoice_repository: InvoiceRepository,
        rpa_service: RpaService | None = None,
    ) -> None:
        self.invoice_repository = invoice_repository
        self.rpa_service = rpa_service or RpaService()

    async def execute(
        self,
        invoice_id: int,
        user: User,
    ) -> RpaExecutionResponse:
        invoice = await self.invoice_repository.get_by_id(invoice_id)
        if invoice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Factura no encontrada.",
            )
        if invoice.status != InvoiceStatus.PROCESSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La factura debe estar procesada antes de ejecutar RPA.",
            )

        try:
            result = await self.rpa_service.register_invoice(invoice)
            await self.invoice_repository.add_log(
                ProcessingLog(
                    invoice_id=invoice.id,
                    user_id=user.id,
                    action="rpa_invoice_registered",
                    status="success",
                    result=(
                        f"Factura registrada mediante RPA. "
                        f"Evidencia: {result.evidence_file}"
                    ),
                )
            )
            return result
        except BusinessRuleError as exc:
            await self.invoice_repository.add_log(
                ProcessingLog(
                    invoice_id=invoice.id,
                    user_id=user.id,
                    action="rpa_invoice_error",
                    status="error",
                    result="La automatización RPA falló.",
                    error_detail=str(exc),
                )
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc
