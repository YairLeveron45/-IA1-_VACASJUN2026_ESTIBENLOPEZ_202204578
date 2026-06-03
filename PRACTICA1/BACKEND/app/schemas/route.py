"""
Modelos de datos usados por el backend.

Estos esquemas validan la informacion que entra y sale de la API.
"""

from pydantic import BaseModel, Field


class RouteQuery(BaseModel):
    """
    Datos minimos para consultar rutas entre dos ciudades.
    """

    origin: str = Field(..., min_length=1, description="Ciudad de origen.")
    destination: str = Field(..., min_length=1, description="Ciudad destino.")


class BestRouteRequest(RouteQuery):
    """
    Hereda los mismos campos de RouteQuery para consultar la mejor ruta.
    """


class RouteResult(BaseModel):
    """
    Representa una ruta concreta y su distancia total.
    """

    route: list[str]
    distance: float


class BestRouteResponse(RouteResult):
    """
    Respuesta de la ruta mas corta.
    """


class AddCityRequest(BaseModel):
    """
    Datos requeridos para agregar una ciudad nueva.
    """

    name: str = Field(..., min_length=1, description="Nombre de la ciudad.")


class AddConnectionRequest(BaseModel):
    """
    Datos requeridos para agregar una conexion nueva.
    """

    origin: str = Field(..., min_length=1, description="Ciudad de origen.")
    destination: str = Field(..., min_length=1, description="Ciudad destino.")
    distance: float = Field(..., gt=0, description="Distancia en kilometros.")


class MessageResponse(BaseModel):
    """
    Respuesta simple para operaciones de alta.
    """

    message: str
