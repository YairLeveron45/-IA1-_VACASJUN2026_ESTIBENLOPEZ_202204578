"""
Servicio de integracion entre Python y Prolog.

Este modulo encapsula todas las consultas al archivo rutas.pl
para que los endpoints no tengan que conocer detalles de Prolog.
"""

import unicodedata
from pathlib import Path

from pyswip import Prolog

from app.schemas.route import BestRouteResponse, RouteResult


class PrologService:
    """
    Capa de servicio encargada de cargar Prolog y ejecutar consultas.
    """

    def __init__(self) -> None:
        """
        Inicializa la conexion con Prolog y carga el archivo de reglas.
        """
        self.prolog = Prolog()
        self.prolog_file = self._get_prolog_file_path()
        self.prolog.consult(str(self.prolog_file))

    def _get_prolog_file_path(self) -> Path:
        """
        Construye la ruta absoluta al archivo rutas.pl.

        Returns:
            Path: ubicacion del archivo Prolog.

        Raises:
            FileNotFoundError: si el archivo no existe.
        """
        prolog_path = Path(__file__).resolve().parents[3] / "PROLOG" / "rutas.pl"
        if not prolog_path.exists():
            raise FileNotFoundError(f"No se encontro el archivo Prolog: {prolog_path}")
        return prolog_path

    def _normalize_city(self, city: str) -> str:
        """
        Normaliza el nombre de ciudad para que coincida con los atomos de Prolog.

        Args:
            city (str): texto recibido desde la API.

        Returns:
            str: ciudad en minusculas y con espacios convertidos a guion bajo.
        """
        normalized = unicodedata.normalize("NFKD", city.strip().lower())
        ascii_city = normalized.encode("ascii", "ignore").decode("ascii")
        return ascii_city.replace(" ", "_")


    def _insert_fact_in_block(self, fact: str, predicate: str) -> None:
        """
        Persiste un hecho Prolog dentro del bloque de su predicado.

        Args:
            fact (str): hecho Prolog sin salto de linea final.
            predicate (str): nombre del predicado, por ejemplo ciudad o conexion.
        """
        lines = self.prolog_file.read_text(encoding="utf-8").splitlines()
        insert_at = None

        for index, line in enumerate(lines):
            stripped_line = line.strip()
            # Solo consideramos hechos de primer nivel, no llamadas dentro de reglas.
            if line == stripped_line and stripped_line.startswith(f"{predicate}("):
                insert_at = index + 1

        if insert_at is None:
            raise ValueError(
                f"No se encontro un bloque para persistir hechos del predicado '{predicate}'."
            )

        lines.insert(insert_at, fact)
        self.prolog_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _run_query(self, query: str) -> list[dict]:
        """
        Ejecuta una consulta en Prolog y devuelve los resultados crudos.

        Args:
            query (str): consulta en sintaxis Prolog.

        Returns:
            list[dict]: resultados producidos por PySwip.
        """
        return list(self.prolog.query(query))

    def _connection_exists(self, origin: str, destination: str) -> bool:
        """
        Verifica si ya existe una conexion directa entre dos ciudades.

        La validacion considera tambien el caso inverso porque las conexiones
        del sistema se tratan como bidireccionales.
        """
        query = f"conexion_existente({origin}, {destination})"
        return bool(self._run_query(query))

    def get_best_route(self, origin: str, destination: str) -> BestRouteResponse:
        """
        Consulta la ruta mas corta entre dos ciudades.

        Args:
            origin (str): ciudad de origen.
            destination (str): ciudad destino.

        Returns:
            BestRouteResponse: mejor ruta y su distancia.

        Raises:
            ValueError: si no existe una ruta valida.
        """
        normalized_origin = self._normalize_city(origin)
        normalized_destination = self._normalize_city(destination)

        query = (
            f"ruta_mas_corta({normalized_origin}, {normalized_destination}, Ruta, Distancia)"
        )
        result = self._run_query(query)

        if not result:
            raise ValueError("No se encontro una ruta entre las ciudades indicadas.")

        best_route = result[0]
        return BestRouteResponse(
            route=self._parse_prolog_list(best_route["Ruta"]),
            distance=float(best_route["Distancia"]),
        )

    def get_cities(self) -> list[str]:
        """
        Obtiene todas las ciudades registradas en la base de conocimiento.

        Returns:
            list[str]: ciudades disponibles ordenadas alfabeticamente.
        """
        result = self._run_query("ciudad(Ciudad)")
        cities = {str(item["Ciudad"]) for item in result}
        return sorted(cities)

    def get_all_routes(self, origin: str, destination: str) -> list[RouteResult]:
        """
        Consulta todas las rutas posibles entre dos ciudades.

        Args:
            origin (str): ciudad de origen.
            destination (str): ciudad destino.

        Returns:
            list[RouteResult]: rutas encontradas ordenadas por distancia.

        Raises:
            ValueError: si no existe ninguna ruta valida.
        """
        normalized_origin = self._normalize_city(origin)
        normalized_destination = self._normalize_city(destination)

        query = (
            f"ruta_con_distancia({normalized_origin}, {normalized_destination}, Ruta, Distancia)"
        )
        result = self._run_query(query)

        if not result:
            raise ValueError("No se encontraron rutas entre las ciudades indicadas.")

        routes = [
            RouteResult(
                route=self._parse_prolog_list(item["Ruta"]),
                distance=float(item["Distancia"]),
            )
            for item in result
        ]
        return sorted(routes, key=lambda route: route.distance)

    def add_city(self, city: str) -> None:
        """
        Agrega una ciudad nueva a la base dinamica de Prolog y la persiste.

        Args:
            city (str): nombre de la ciudad.

        Raises:
            ValueError: si Prolog no pudo registrar la ciudad.
        """
        normalized_city = self._normalize_city(city)

        if normalized_city in self.get_cities():
            raise ValueError("No fue posible agregar la ciudad. Revisa si ya existe.")

        result = self._run_query(f"agregar_ciudad({normalized_city})")

        if not result:
            raise ValueError("No fue posible agregar la ciudad. Revisa si ya existe.")

        self._insert_fact_in_block(f"ciudad({normalized_city}).", "ciudad")

    def add_connection(self, origin: str, destination: str, distance: float) -> None:
        """
        Agrega una conexion nueva a la base dinamica de Prolog y la persiste.

        Args:
            origin (str): ciudad de origen.
            destination (str): ciudad destino.
            distance (float): distancia en kilometros.

        Raises:
            ValueError: si Prolog no pudo registrar la conexion.
        """
        normalized_origin = self._normalize_city(origin)
        normalized_destination = self._normalize_city(destination)

        if normalized_origin == normalized_destination:
            raise ValueError("El origen y el destino deben ser ciudades distintas.")

        if self._connection_exists(normalized_origin, normalized_destination):
            raise ValueError(
                "Ya existe una conexion entre esas ciudades. No se permiten duplicados."
            )

        result = self._run_query(
            "agregar_conexion("
            f"{normalized_origin}, {normalized_destination}, {distance}"
            ")"
        )

        if not result:
            raise ValueError(
                "No fue posible agregar la conexion. Verifica ciudades y distancia."
            )

        self._insert_fact_in_block(
            f"conexion({normalized_origin}, {normalized_destination}, {distance}).",
            "conexion",
        )

    def _parse_prolog_list(self, prolog_list: object) -> list[str]:
        """
        Convierte la lista devuelta por Prolog a una lista de cadenas en Python.

        Args:
            prolog_list (object): estructura retornada por PySwip.

        Returns:
            list[str]: contenido de la ruta en formato amigable.
        """
        return [str(item) for item in prolog_list]
