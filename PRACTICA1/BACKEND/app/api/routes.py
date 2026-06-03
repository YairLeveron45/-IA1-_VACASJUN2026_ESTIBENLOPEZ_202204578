"""
Endpoints del backend.

Aqui se reciben solicitudes HTTP y se delega el trabajo real
al servicio que consulta Prolog.
"""

from fastapi import APIRouter, HTTPException

from app.schemas.route import (
    AddConnectionRequest,
    AddCityRequest,
    BestRouteRequest,
    BestRouteResponse,
    MessageResponse,
    RouteQuery,
    RouteResult,
)
from app.services.prolog_service import PrologService


router = APIRouter()
prolog_service = PrologService()


@router.get("/cities", response_model=list[str])
def get_cities() -> list[str]:
    """
    Devuelve todas las ciudades disponibles para poblar selectores en el frontend.

    Returns:
        list[str]: listado simple de ciudades.
    """
    return prolog_service.get_cities()


@router.post("/best-route", response_model=BestRouteResponse)
def get_best_route(request: BestRouteRequest) -> BestRouteResponse:
    """
    Obtiene la ruta mas corta entre dos ciudades.

    Args:
        request (BestRouteRequest): ciudades de origen y destino.

    Returns:
        BestRouteResponse: mejor ruta encontrada y su distancia total.
    """
    try:
        return prolog_service.get_best_route(request.origin, request.destination)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/routes", response_model=list[RouteResult])
def get_all_routes(request: RouteQuery) -> list[RouteResult]:
    """
    Devuelve todas las rutas posibles entre dos ciudades.

    Args:
        request (RouteQuery): ciudades de origen y destino.

    Returns:
        list[RouteResult]: lista de rutas con su distancia total.
    """
    try:
        return prolog_service.get_all_routes(request.origin, request.destination)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/cities", response_model=MessageResponse)
def add_city(request: AddCityRequest) -> MessageResponse:
    """
    Agrega una ciudad nueva a la base de conocimiento.

    Args:
        request (AddCityRequest): nombre de la ciudad.

    Returns:
        MessageResponse: mensaje indicando el resultado.
    """
    try:
        prolog_service.add_city(request.name)
        return MessageResponse(message=f"Ciudad '{request.name}' agregada correctamente.")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/connections", response_model=MessageResponse)
def add_connection(request: AddConnectionRequest) -> MessageResponse:
    """
    Agrega una conexion nueva entre dos ciudades.

    Args:
        request (AddConnectionRequest): origen, destino y distancia.

    Returns:
        MessageResponse: mensaje indicando el resultado.
    """
    try:
        prolog_service.add_connection(
            request.origin,
            request.destination,
            request.distance,
        )
        return MessageResponse(message="Conexion agregada correctamente.")
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
