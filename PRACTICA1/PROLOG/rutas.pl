% Practica 1
% Ruta mas corta entre ciudades usando Prolog.

:- dynamic ciudad/1.
:- dynamic conexion/3.

% Ciudades disponibles en la base de conocimiento.
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

% Conexiones directas entre ciudades y su distancia en kilometros.
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

% Las carreteras se consideran bidireccionales.
conectadas(Ciudad1, Ciudad2, Distancia) :-
    conexion(Ciudad1, Ciudad2, Distancia).
conectadas(Ciudad1, Ciudad2, Distancia) :-
    conexion(Ciudad2, Ciudad1, Distancia).

% Ruta directa entre origen y destino.
ruta(Origen, Destino, [Origen, Destino]) :-
    conectadas(Origen, Destino, _).

% Ruta compuesta evitando repetir ciudades.
ruta(Origen, Destino, [Origen | Ruta]) :-
    Origen \= Destino,
    recorrer(Origen, Destino, [Origen], Ruta).

recorrer(Actual, Destino, Visitadas, [Destino]) :-
    conectadas(Actual, Destino, _),
    \+ member(Destino, Visitadas).

recorrer(Actual, Destino, Visitadas, [Siguiente | Ruta]) :-
    conectadas(Actual, Siguiente, _),
    Siguiente \= Destino,
    \+ member(Siguiente, Visitadas),
    recorrer(Siguiente, Destino, [Siguiente | Visitadas], Ruta).

% Calcula la distancia total de una ruta.
distancia_ruta([_], 0).
distancia_ruta([Ciudad1, Ciudad2 | Resto], DistanciaTotal) :-
    conectadas(Ciudad1, Ciudad2, DistanciaTramo),
    distancia_ruta([Ciudad2 | Resto], DistanciaRestante),
    DistanciaTotal is DistanciaTramo + DistanciaRestante.

% Devuelve una ruta valida junto con su distancia total.
ruta_con_distancia(Origen, Destino, Ruta, Distancia) :-
    ruta(Origen, Destino, Ruta),
    distancia_ruta(Ruta, Distancia).

% Reune todas las rutas posibles entre dos ciudades.
todas_las_rutas(Origen, Destino, Rutas) :-
    findall(
        ruta_distancia(Ruta, Distancia),
        ruta_con_distancia(Origen, Destino, Ruta, Distancia),
        Rutas
    ).

% Obtiene la ruta mas corta entre dos ciudades.
ruta_mas_corta(Origen, Destino, MejorRuta, MejorDistancia) :-
    setof(
        Distancia-Ruta,
        ruta_con_distancia(Origen, Destino, Ruta, Distancia),
        [MejorDistancia-MejorRuta | _]
    ).

% Permite agregar una nueva ciudad desde la aplicacion.
agregar_ciudad(Ciudad) :-
    \+ ciudad(Ciudad),
    assertz(ciudad(Ciudad)).

% Permite agregar una nueva conexion desde la aplicacion.
agregar_conexion(Origen, Destino, Distancia) :-
    ciudad(Origen),
    ciudad(Destino),
    Distancia > 0,
    \+ conexion(Origen, Destino, Distancia),
    assertz(conexion(Origen, Destino, Distancia)).
