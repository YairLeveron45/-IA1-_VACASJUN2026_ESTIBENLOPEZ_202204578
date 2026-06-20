from pathlib import Path

from fastapi import UploadFile

from app.core.exceptions import BusinessRuleError, ResourceNotFoundError
from app.models.invoice_model import Invoice, InvoiceStatus
from app.models.processing_log_model import ProcessingLog
from app.models.provider_model import Provider
from app.models.user_model import User
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.provider_repository import ProviderRepository
from app.schemas.invoice_schema import InvoiceValidationRequest
from app.services.file_storage_service import FileStorageService
from app.services.invoice_extraction_service import InvoiceExtractionService
from app.services.ocr_service import OcrService
from app.schemas.ocr_schema import OcrProcessingResponse


class InvoiceService:
    """Coordina almacenamiento, OCR, validación y persistencia de facturas."""

    def __init__(
        self,
        repository: InvoiceRepository,
        storage: FileStorageService | None = None,
        ocr: OcrService | None = None,
        extractor: InvoiceExtractionService | None = None,
        provider_repository: ProviderRepository | None = None,
    ) -> None:
        """Inicializa el servicio y permite sustituir dependencias en pruebas."""
        self.repository = repository
        self.storage = storage or FileStorageService()
        self.ocr = ocr or OcrService()
        self.extractor = extractor or InvoiceExtractionService()
        self.provider_repository = provider_repository

    async def list(
        self,
        page: int,
        page_size: int,
        status: InvoiceStatus | None,
        provider_id: int | None,
        search: str | None = None,
    ) -> tuple[list[Invoice], int]:
        """Lista facturas aplicando paginación y filtros opcionales."""
        offset = (page - 1) * page_size
        return await self.repository.list(
            offset,
            page_size,
            status,
            provider_id,
            search,
        )

    async def get(self, invoice_id: int) -> Invoice:
        """Obtiene una factura activa o informa que no existe."""
        invoice = await self.repository.get_by_id(invoice_id)
        if invoice is None:
            raise ResourceNotFoundError("Factura no encontrada.")
        return invoice

    async def upload(self, file: UploadFile, user: User) -> Invoice:
        """Guarda el archivo y crea la factura pendiente con su bitácora."""
        original_name, stored_path, content_type = (
            await self.storage.save_invoice(file)
        )
        invoice = Invoice(
            file_name=original_name,
            file_path=stored_path,
            content_type=content_type,
            status=InvoiceStatus.PENDING,
            uploaded_by_id=user.id,
        )
        log = ProcessingLog(
            user_id=user.id,
            action="invoice_upload",
            status=InvoiceStatus.PENDING.value,
            result=f"Archivo cargado: {original_name}",
        )

        try:
            return await self.repository.create_with_log(invoice, log)
        except Exception:
            # Si la base de datos falla, elimina el archivo para no dejar residuos.
            self.storage.delete(stored_path)
            raise

    async def get_download(self, invoice_id: int) -> tuple[Invoice, Path]:
        """Valida y devuelve la ruta segura del documento original."""
        invoice = await self.get(invoice_id)
        return invoice, self.storage.get_existing_path(invoice.file_path)

    async def reject(self, invoice_id: int, user: User) -> Invoice:
        """Rechaza una factura únicamente cuando su estado lo permite."""
        invoice = await self.get(invoice_id)
        if invoice.status == InvoiceStatus.REJECTED:
            raise BusinessRuleError("La factura ya está rechazada.")
        if invoice.status == InvoiceStatus.PROCESSED:
            raise BusinessRuleError(
                "Una factura procesada no puede rechazarse."
            )

        invoice.status = InvoiceStatus.REJECTED
        log = ProcessingLog(
            invoice_id=invoice.id,
            user_id=user.id,
            action="invoice_rejected",
            status=InvoiceStatus.REJECTED.value,
            result="La factura fue rechazada por el usuario.",
        )
        return await self.repository.update_with_log(invoice, log)

    async def delete(self, invoice_id: int, user: User) -> Invoice:
        """Aplica borrado lógico, conserva la bitácora y retira el archivo."""
        invoice = await self.get(invoice_id)
        invoice.is_deleted = True
        log = ProcessingLog(
            invoice_id=invoice.id,
            user_id=user.id,
            action="invoice_deleted",
            status="success",
            result=(
                f"Factura eliminada lógicamente: {invoice.file_name}. "
                "La bitácora se conserva."
            ),
        )
        invoice = await self.repository.update_with_log(invoice, log)
        self.storage.delete(invoice.file_path)
        return invoice

    async def process(
        self,
        invoice_id: int,
        user: User,
    ) -> OcrProcessingResponse:
        """Ejecuta OCR, extrae campos y registra el resultado o el error."""
        invoice = await self.get(invoice_id)
        if invoice.status == InvoiceStatus.REJECTED:
            raise BusinessRuleError(
                "Una factura rechazada no puede procesarse."
            )

        path = self.storage.get_existing_path(invoice.file_path)
        try:
            text, pages_processed = self.ocr.extract_text(path)
            if not text.strip():
                raise BusinessRuleError(
                    "El OCR no pudo extraer texto del documento."
                )

            extracted, warnings = self.extractor.extract(text)
            invoice.ocr_text = text
            invoice.invoice_number = extracted.invoice_number
            invoice.invoice_date = self.extractor.parse_date(
                extracted.invoice_date
            )
            invoice.detected_provider_name = extracted.provider_name
            invoice.detected_nit = extracted.nit
            invoice.subtotal = self.extractor.parse_amount(extracted.subtotal)
            invoice.taxes = self.extractor.parse_amount(extracted.taxes)
            invoice.total = self.extractor.parse_amount(extracted.total)
            invoice.status = (
                InvoiceStatus.PROCESSED
                if not warnings
                else InvoiceStatus.ERROR
            )
            log = ProcessingLog(
                invoice_id=invoice.id,
                user_id=user.id,
                action="invoice_ocr_processed",
                status=invoice.status.value,
                result=(
                    f"OCR completado en {pages_processed} página(s). "
                    f"Advertencias: {len(warnings)}."
                ),
            )
            invoice = await self.repository.update_with_log(invoice, log)
            return OcrProcessingResponse(
                invoice=invoice,
                extracted=extracted,
                warnings=warnings,
                pages_processed=pages_processed,
            )
        except BusinessRuleError:
            # Los errores esperados conservan su mensaje para informar al usuario.
            raise
        except Exception as exc:
            # Los fallos inesperados quedan auditados sin exponer detalles internos.
            invoice.status = InvoiceStatus.ERROR
            log = ProcessingLog(
                invoice_id=invoice.id,
                user_id=user.id,
                action="invoice_ocr_error",
                status=InvoiceStatus.ERROR.value,
                result="No fue posible procesar la factura.",
                error_detail=str(exc),
            )
            await self.repository.update_with_log(invoice, log)
            raise BusinessRuleError(
                "Ocurrió un error durante el procesamiento OCR."
            ) from exc

    async def validate_manually(
        self,
        invoice_id: int,
        data: InvoiceValidationRequest,
        user: User,
    ) -> Invoice:
        """Guarda correcciones manuales y asocia o crea el proveedor por NIT."""
        invoice = await self.get(invoice_id)
        if invoice.status == InvoiceStatus.REJECTED:
            raise BusinessRuleError(
                "Una factura rechazada no puede validarse."
            )

        provider_id = None
        provider_created = False
        provider_message = "No se encontró un proveedor registrado con ese NIT."
        if self.provider_repository is not None:
            provider = await self.provider_repository.get_by_nit(data.nit)
            if provider is not None:
                if not provider.is_active:
                    raise BusinessRuleError(
                        "El proveedor asociado se encuentra desactivado."
                    )
                provider_id = provider.id
                provider_message = (
                    f"Proveedor asociado: {provider.name} ({provider.nit})."
                )
            elif data.create_provider_if_missing:
                provider = await self.provider_repository.create_pending(
                    Provider(name=data.provider_name, nit=data.nit)
                )
                provider_id = provider.id
                provider_created = True
                provider_message = (
                    f"Proveedor creado y asociado: {provider.name} "
                    f"({provider.nit})."
                )

        invoice.invoice_number = data.invoice_number
        invoice.invoice_date = data.invoice_date
        invoice.provider_id = provider_id
        invoice.detected_provider_name = data.provider_name
        invoice.detected_nit = data.nit
        invoice.subtotal = data.subtotal
        invoice.taxes = data.taxes
        invoice.total = data.total
        invoice.status = InvoiceStatus.PROCESSED

        logs = [ProcessingLog(
            invoice_id=invoice.id,
            user_id=user.id,
            action="invoice_manually_validated",
            status=InvoiceStatus.PROCESSED.value,
            result=(
                "Datos de factura corregidos y validados manualmente. "
                f"{provider_message}"
            ),
        )]
        if provider_created:
            logs.append(
                ProcessingLog(
                    user_id=user.id,
                    action="provider_created",
                    status="success",
                    result=provider_message,
                )
            )
        return await self.repository.update_with_logs(invoice, logs)
