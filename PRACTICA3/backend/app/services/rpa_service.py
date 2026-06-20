import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from playwright.async_api import Error as PlaywrightError
from playwright.async_api import async_playwright

from app.core.config import settings
from app.core.exceptions import BusinessRuleError
from app.models.invoice_model import Invoice
from app.schemas.rpa_schema import RpaExecutionResponse


class RpaService:
    """Automatiza el formulario contable y guarda evidencia de ejecución."""

    def __init__(self, output_directory: str | None = None) -> None:
        self.output_directory = Path(
            output_directory or settings.rpa_output_directory
        ).resolve()
        self.output_directory.mkdir(parents=True, exist_ok=True)

    async def register_invoice(self, invoice: Invoice) -> RpaExecutionResponse:
        """Completa el formulario mediante Playwright y registra el resultado."""
        execution_id = uuid4().hex
        screenshot = self.output_directory / f"rpa-{execution_id}.png"
        evidence = self.output_directory / f"rpa-{execution_id}.json"
        executed_at = datetime.now(UTC)

        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(
                    headless=True,
                    executable_path=settings.rpa_browser_executable,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )
                page = await browser.new_page(viewport={"width": 1280, "height": 900})
                await page.goto(
                    settings.rpa_target_url,
                    wait_until="networkidle",
                    timeout=30_000,
                )
                await page.fill("#invoice_number", invoice.invoice_number or "")
                await page.fill(
                    "#invoice_date",
                    invoice.invoice_date.isoformat() if invoice.invoice_date else "",
                )
                await page.fill(
                    "#provider_name",
                    invoice.detected_provider_name or "",
                )
                await page.fill("#nit", invoice.detected_nit or "")
                await page.fill("#subtotal", self._money(invoice.subtotal))
                await page.fill("#taxes", self._money(invoice.taxes))
                await page.fill("#total", self._money(invoice.total))
                await page.click("#submit-button")
                await page.wait_for_selector("#confirmation", timeout=15_000)
                confirmation = (await page.text_content("#confirmation") or "").strip()
                result_url = page.url
                await page.screenshot(path=str(screenshot), full_page=True)
                await browser.close()
        except PlaywrightError as exc:
            # Oculta detalles del navegador y devuelve un error de negocio claro.
            raise BusinessRuleError(
                "La automatización RPA no pudo completar el formulario."
            ) from exc

        payload = {
            "invoice_id": invoice.id,
            "target_url": result_url,
            "confirmation": confirmation,
            "screenshot": str(screenshot),
            "executed_at": executed_at.isoformat(),
            "fields": {
                "invoice_number": invoice.invoice_number,
                "invoice_date": (
                    invoice.invoice_date.isoformat() if invoice.invoice_date else None
                ),
                "provider_name": invoice.detected_provider_name,
                "nit": invoice.detected_nit,
                "subtotal": self._money(invoice.subtotal),
                "taxes": self._money(invoice.taxes),
                "total": self._money(invoice.total),
            },
        }
        evidence.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return RpaExecutionResponse(
            success=True,
            invoice_id=invoice.id,
            target_url=result_url,
            confirmation=confirmation,
            evidence_file=str(evidence),
            executed_at=executed_at,
        )

    def _money(self, value) -> str:
        """Formatea montos para los campos HTML del formulario."""
        return f"{value:.2f}" if value is not None else ""
