from html import escape
from typing import Annotated

from fastapi import APIRouter, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.services.rpa_simulator_service import RpaSimulatorService


router = APIRouter(prefix="/rpa-simulator", tags=["RPA simulator"])
simulator = RpaSimulatorService()


@router.get("/form", response_class=HTMLResponse, include_in_schema=False)
async def simulator_form() -> HTMLResponse:
    return HTMLResponse(
        """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Sistema contable simulado</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 720px; margin: 30px auto; }
    label { display: block; margin-top: 12px; font-weight: bold; }
    input { width: 100%; padding: 8px; box-sizing: border-box; }
    button { margin-top: 18px; padding: 10px 18px; }
  </style>
</head>
<body>
  <h1>Registro contable simulado</h1>
  <form method="post" action="/api/v1/rpa-simulator/submit">
    <label>Número de factura<input id="invoice_number" name="invoice_number"></label>
    <label>Fecha<input id="invoice_date" name="invoice_date" type="date"></label>
    <label>Proveedor<input id="provider_name" name="provider_name"></label>
    <label>NIT<input id="nit" name="nit"></label>
    <label>Subtotal<input id="subtotal" name="subtotal"></label>
    <label>Impuestos<input id="taxes" name="taxes"></label>
    <label>Total<input id="total" name="total"></label>
    <button id="submit-button" type="submit">Registrar factura</button>
  </form>
</body>
</html>
        """
    )


@router.post("/submit", include_in_schema=False)
async def simulator_submit(
    invoice_number: Annotated[str, Form()],
    invoice_date: Annotated[str, Form()],
    provider_name: Annotated[str, Form()],
    nit: Annotated[str, Form()],
    subtotal: Annotated[str, Form()],
    taxes: Annotated[str, Form()],
    total: Annotated[str, Form()],
) -> RedirectResponse:
    registration_id = simulator.save_submission(
        {
            "invoice_number": invoice_number,
            "invoice_date": invoice_date,
            "provider_name": provider_name,
            "nit": nit,
            "subtotal": subtotal,
            "taxes": taxes,
            "total": total,
        }
    )
    return RedirectResponse(
        url=f"/api/v1/rpa-simulator/result/{registration_id}",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/result/{registration_id}",
    response_class=HTMLResponse,
    include_in_schema=False,
)
async def simulator_result(registration_id: str) -> HTMLResponse:
    submission = simulator.get_submission(registration_id)
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Registro simulado no encontrado.",
        )
    fields = submission["fields"]
    rows = [
        ("Número de factura", fields["invoice_number"]),
        ("Fecha", fields["invoice_date"]),
        ("Proveedor", fields["provider_name"]),
        ("NIT", fields["nit"]),
        ("Subtotal", fields["subtotal"]),
        ("Impuestos", fields["taxes"]),
        ("Total", fields["total"]),
    ]
    field_rows = "".join(
        f"<div><span>{escape(label)}</span><strong>{escape(value)}</strong></div>"
        for label, value in rows
    )
    return HTMLResponse(
        f"""
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Factura registrada - Sistema contable simulado</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; min-height: 100vh; display: grid; place-items: center;
      padding: 32px; font-family: Arial, sans-serif; color: #172033;
      background: #f4f6fa;
    }}
    main {{
      width: min(720px, 100%); padding: 32px; border: 1px solid #e1e5ee;
      border-radius: 18px; background: white;
      box-shadow: 0 18px 50px rgba(27, 37, 61, .09);
    }}
    .success {{
      width: 50px; height: 50px; display: grid; place-items: center;
      border-radius: 15px; color: white; background: #28a57a;
      font-size: 25px; font-weight: bold;
    }}
    h1 {{ margin: 18px 0 8px; font-size: 27px; }}
    p {{ margin: 0 0 24px; color: #6f788b; }}
    section {{
      display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
    }}
    section div {{
      padding: 14px; border: 1px solid #e7eaf1; border-radius: 11px;
      background: #fafbfe;
    }}
    section span, section strong {{ display: block; }}
    section span {{ color: #7c8597; font-size: 12px; }}
    section strong {{ margin-top: 5px; font-size: 15px; }}
    footer {{
      margin-top: 22px; padding-top: 18px; border-top: 1px solid #e7eaf1;
      color: #8a92a3; font-size: 11px;
    }}
    @media (max-width: 560px) {{
      body {{ padding: 16px; }}
      main {{ padding: 22px; }}
      section {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <div class="success">✓</div>
    <h1 id="confirmation">Factura registrada correctamente</h1>
    <p>El robot completó y envió la información al sistema contable simulado.</p>
    <section>{field_rows}</section>
    <footer>Identificador del registro: {escape(registration_id)}</footer>
  </main>
</body>
</html>
        """
    )
