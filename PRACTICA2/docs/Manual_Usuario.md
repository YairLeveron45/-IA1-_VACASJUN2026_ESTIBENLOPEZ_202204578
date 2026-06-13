# Manual de Usuario - SmartBot

## Inicio de sesion

1. Abre `http://localhost:5173`.
2. Ingresa con:

```txt
Usuario: IA1-User
Contrasena: IA1-password@_new
```

## Gestionar preguntas

1. Entra a la opcion `Preguntas`.
2. Escribe la pregunta, respuesta y categoria.
3. Presiona `Crear pregunta`.
4. Para modificar una pregunta existente, edita sus campos y presiona `Guardar`.
5. Para eliminarla, presiona `Eliminar`.

## Gestionar categorias

1. Entra a `Categorias`.
2. Escribe nombre y descripcion.
3. Presiona `Crear`.

## Configuracion de Telegram

1. Entra a `Configuracion`.
2. Escribe el ID del chat o grupo de Telegram.
3. Presiona `Guardar configuracion`.

## Uso del bot

1. Crea un bot en Telegram con BotFather.
2. Copia el token en el archivo `.env`.
3. Levanta el proyecto con el perfil del bot.
4. Escribe una consulta al bot, por ejemplo:

```txt
Cual es el horario de atencion?
```

El bot respondera usando la informacion registrada en la base de datos.
