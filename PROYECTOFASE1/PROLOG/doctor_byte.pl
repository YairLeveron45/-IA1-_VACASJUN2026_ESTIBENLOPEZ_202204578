% Archivo principal del sistema experto Doctor Byte.
% Aqui se pueden cargar sintomas, fallas, recomendaciones y reglas.

:- consult('sintomas.pl').
:- consult('fallas.pl').
:- consult('recomendaciones.pl').

% Regla auxiliar para verificar si un sintoma fue reportado.
presenta(SintomasSeleccionados, Sintoma) :-
    member(Sintoma, SintomasSeleccionados).

% Regla auxiliar para verificar si todos los sintomas de una lista fueron reportados.
presenta_todos(_, []).
presenta_todos(SintomasSeleccionados, [Sintoma | Resto]) :-
    presenta(SintomasSeleccionados, Sintoma),
    presenta_todos(SintomasSeleccionados, Resto).

% Reglas de inferencia.
regla_diagnostico(
    bateria_defectuosa,
    [bateria_no_carga, no_enciende]
).

regla_diagnostico(
    celdas_internas_danadas_que_ya_no_pueden_almacenar_energia_quimica_de_forma_eficiente,
    [bateria_se_descarga_rapido, se_apaga_inesperadamente]
).

regla_diagnostico(
    controlador_red_danado,
    [no_detecta_wifi, internet_lento]
).

regla_diagnostico(
    degradacion_o_dano_en_el_disco_duro,
    [lentitud_extrema_al_abrir_archivos, pantalla_azul]
).

regla_diagnostico(
    disco_duro_danado,
    [ruido_disco, archivos_corruptos]
).

regla_diagnostico(
    error_sistema_operativo,
    [error_arranque, pantalla_azul]
).

regla_diagnostico(
    falla_en_el_cable_flex_o_cinta_de_video,
    [parpadeos_o_lineas_de_colores, pantalla_negra]
).

regla_diagnostico(
    fallo_memoria_ram,
    [pitidos_al_arrancar, congelamientos_frecuentes]
).

regla_diagnostico(
    fallo_tarjeta_grafica,
    [pantalla_negra, pitidos_al_arrancar]
).

regla_diagnostico(
    fuente_de_poder_insuficiente,
    [reinicios_inesperados, sobrecalentamiento]
).

regla_diagnostico(
    infeccion_malware,
    [lentitud_general, programas_se_cierran]
).

regla_diagnostico(
    problema_fuente_poder,
    [no_enciende, pantalla_negra]
).

regla_diagnostico(
    puertos_usb_danados,
    [usb_no_detecta, perifericos_no_responden]
).

regla_diagnostico(
    sobrecalentamiento_cpu,
    [sobrecalentamiento, ventilador_ruidoso]
).

% Predicado principal: recibe una lista de sintomas y devuelve una falla.
% El corte evita seguir buscando si ya se encontro el primer diagnostico valido.
diagnosticar(SintomasSeleccionados, Falla) :-
    regla_diagnostico(Falla, SintomasClave),
    presenta_todos(SintomasSeleccionados, SintomasClave),
    !.

% Devuelve falla y recomendacion en una sola consulta.
diagnostico_con_recomendacion(SintomasSeleccionados, Falla, Recomendacion) :-
    diagnosticar(SintomasSeleccionados, Falla),
    recomendacion(Falla, Recomendacion).

% Permite listar las fallas conocidas por el sistema.
falla_diagnosticable(Falla) :-
    falla(Falla).

% Devuelve una lista de todos los sintomas registrados.
listar_sintomas(ListaSintomas) :-
    findall(Sintoma, sintoma(Sintoma), ListaSintomas).
