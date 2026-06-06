% ============================================================================
% Practica 1
% Sistema de rutas entre ciudades usando Prolog
%
% Este archivo funciona como la base de conocimiento del proyecto.
% Aqui se definen:
% 1. Las ciudades disponibles
% 2. Las conexiones directas entre ciudades y su distancia
% 3. Las reglas para buscar rutas
% 4. Las reglas para calcular distancias
% 5. Las reglas para encontrar la ruta mas corta
% 6. Las reglas para agregar ciudades y conexiones dinamicamente
% ============================================================================

:- dynamic ciudad/1.
:- dynamic conexion/3.

% ============================================================================
% HECHOS: CIUDADES
% Cada hecho ciudad/1 representa una ciudad disponible en el sistema.
% Ejemplo:
%   ciudad(guatemala).
% significa: "la ciudad guatemala existe en la base de conocimiento".
% ============================================================================

ciudad(guatemala).
ciudad(antigua).
ciudad(escuintla).
ciudad(coban).
ciudad(quetzaltenango).
ciudad(huehuetenango).
ciudad(puerto_barrios).
ciudad(chiquimula).
ciudad(jalapa).
ciudad(peten).
ciudad(miami).
ciudad(espana).
ciudad(el_salvador).
ciudad(santa_rosa).
ciudad(irtra).
ciudad(colonia_villa_sol).
ciudad(totonicapan).
ciudad(villa_nueva).

% ============================================================================
% HECHOS: CONEXIONES
% Cada hecho conexion/3 representa una conexion directa entre dos ciudades.
% Formato:
%   conexion(Origen, Destino, Distancia).
%
% Ejemplo:
%   conexion(guatemala, antigua, 40).
% significa: "existe una conexion directa entre guatemala y antigua
% con una distancia de 40 kilometros".
% ============================================================================

conexion(guatemala, antigua, 40).
conexion(guatemala, escuintla, 60).
conexion(guatemala, coban, 215).
conexion(guatemala, jalapa, 114).
conexion(guatemala, chiquimula, 172).
conexion(antigua, escuintla, 40).
conexion(escuintla, quetzaltenango, 155).
conexion(quetzaltenango, huehuetenango, 86).
conexion(coban, peten, 267).
conexion(coban, puerto_barrios, 285).
conexion(chiquimula, puerto_barrios, 194).
conexion(chiquimula, jalapa, 95).
conexion(jalapa, antigua, 137).
conexion(peten, huehuetenango, 424).
conexion(escuintla, puerto_barrios, 350).
conexion(miami, espana, 58.0).
conexion(el_salvador, santa_rosa, 60.0).
conexion(irtra, colonia_villa_sol, 90.0).
conexion(totonicapan, villa_nueva, 100.0).
conexion(peten, guatemala, 45.0).

% ============================================================================
% REGLA: CONEXIONES BIDIRECCIONALES
%
% Aunque la base de conocimiento almacena una conexion en un solo sentido,
% esta regla permite que el sistema la considere en ambos sentidos.
%
% Ejemplo:
% Si existe conexion(guatemala, antigua, 40), entonces tambien se podra
% consultar como si existiera una conexion de antigua a guatemala.
% ============================================================================

conectadas(Ciudad1, Ciudad2, Distancia) :-
    conexion(Ciudad1, Ciudad2, Distancia).
conectadas(Ciudad1, Ciudad2, Distancia) :-
    conexion(Ciudad2, Ciudad1, Distancia).

% ============================================================================
% REGLAS DE BUSQUEDA DE RUTAS
% ============================================================================

% Caso base:
% Si origen y destino estan conectados directamente, la ruta es simplemente
% [Origen, Destino].
ruta(Origen, Destino, [Origen, Destino]) :-
    conectadas(Origen, Destino, _).

% Caso recursivo:
% Si no existe una ruta directa suficiente, se inicia una busqueda recursiva.
% Se comienza con la ciudad de origen como ya visitada para evitar ciclos.
ruta(Origen, Destino, [Origen | Ruta]) :-
    Origen \= Destino,
    recorrer(Origen, Destino, [Origen], Ruta).

% Caso base del recorrido:
% Si la ciudad actual esta conectada con el destino y el destino aun no fue
% visitado, entonces se completa la ruta.
recorrer(Actual, Destino, Visitadas, [Destino]) :-
    conectadas(Actual, Destino, _),
    \+ member(Destino, Visitadas).

% Caso recursivo del recorrido:
% 1. Desde la ciudad actual se busca una ciudad siguiente conectada.
% 2. Esa ciudad siguiente no debe ser el destino todavia.
% 3. Tampoco debe haberse visitado antes.
% 4. Se continua la busqueda agregando la nueva ciudad a la lista de visitadas.
%
% Esto evita ciclos como:
% guatemala -> antigua -> guatemala -> antigua ...
recorrer(Actual, Destino, Visitadas, [Siguiente | Ruta]) :-
    conectadas(Actual, Siguiente, _),
    Siguiente \= Destino,
    \+ member(Siguiente, Visitadas),
    recorrer(Siguiente, Destino, [Siguiente | Visitadas], Ruta).

% ============================================================================
% CALCULO DE DISTANCIA
% ============================================================================

% Caso base:
% Una ruta con una sola ciudad no tiene distancia acumulada.
distancia_ruta([_], 0).

% Caso recursivo:
% 1. Toma dos ciudades consecutivas de la ruta.
% 2. Busca la distancia directa entre ambas.
% 3. Calcula la distancia del resto de la ruta.
% 4. Suma ambos valores.
distancia_ruta([Ciudad1, Ciudad2 | Resto], DistanciaTotal) :-
    conectadas(Ciudad1, Ciudad2, DistanciaTramo),
    distancia_ruta([Ciudad2 | Resto], DistanciaRestante),
    DistanciaTotal is DistanciaTramo + DistanciaRestante.

% Esta regla combina la busqueda de una ruta con el calculo de su distancia.
% Devuelve una ruta valida junto con la distancia total recorrida.
ruta_con_distancia(Origen, Destino, Ruta, Distancia) :-
    ruta(Origen, Destino, Ruta),
    distancia_ruta(Ruta, Distancia).

% Reune todas las rutas posibles entre dos ciudades.
% findall/3 recopila todos los resultados que satisfacen la consulta.
todas_las_rutas(Origen, Destino, Rutas) :-
    findall(
        ruta_distancia(Ruta, Distancia),
        ruta_con_distancia(Origen, Destino, Ruta, Distancia),
        Rutas
    ).

% Obtiene automaticamente la ruta mas corta.
%
% setof/3 ordena los resultados por la primera parte del termino
% Distancia-Ruta, por eso el primer elemento de la lista es la ruta
% con menor distancia total.
ruta_mas_corta(Origen, Destino, MejorRuta, MejorDistancia) :-
    setof(
        Distancia-Ruta,
        ruta_con_distancia(Origen, Destino, Ruta, Distancia),
        [MejorDistancia-MejorRuta | _]
    ).

% ============================================================================
% REGLAS DINAMICAS PARA ACTUALIZAR LA BASE DE CONOCIMIENTO
% ============================================================================

% Agrega una ciudad solo si todavia no existe.
% assertz/1 inserta el hecho en memoria al final de la base de conocimiento.
agregar_ciudad(Ciudad) :-
    \+ ciudad(Ciudad),
    assertz(ciudad(Ciudad)).

% Indica si ya existe una conexion directa entre dos ciudades,
% sin importar el orden en el que se consulte.
conexion_existente(Origen, Destino) :-
    conexion(Origen, Destino, _).
conexion_existente(Origen, Destino) :-
    conexion(Destino, Origen, _).

% Agrega una conexion solo si:
% 1. ambas ciudades existen
% 2. origen y destino son distintos
% 3. la distancia es mayor que cero
% 4. no existe ya una conexion entre ambas ciudades, ni en el mismo
%    orden ni en el inverso
%
% Luego se inserta en memoria usando assertz/1.
agregar_conexion(Origen, Destino, Distancia) :-
    ciudad(Origen),
    ciudad(Destino),
    Origen \= Destino,
    Distancia > 0,
    \+ conexion_existente(Origen, Destino),
    assertz(conexion(Origen, Destino, Distancia)).
