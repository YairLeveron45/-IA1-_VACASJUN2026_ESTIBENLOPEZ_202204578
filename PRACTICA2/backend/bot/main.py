import os

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

API_URL = os.getenv("API_URL", "http://web:8000")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


async def get_configured_chat_id(client: httpx.AsyncClient) -> str:
    response = await client.get(f"{API_URL}/api/bot/settings")
    response.raise_for_status()
    return str(response.json().get("telegram_chat_id", "")).strip()


def current_chat_id(update: Update) -> str:
    return str(update.effective_chat.id) if update.effective_chat else ""


async def is_authorized_chat(update: Update, client: httpx.AsyncClient) -> bool:
    try:
        configured_chat_id = await get_configured_chat_id(client)
    except httpx.HTTPError:
        return False
    return bool(configured_chat_id) and current_chat_id(update) == configured_chat_id


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        if await is_authorized_chat(update, client):
            await update.message.reply_text("Hola, soy SmartBot. Escribe una pregunta y buscare una respuesta.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        if await is_authorized_chat(update, client):
            await update.message.reply_text("Puedes escribirme consultas como: Cual es el horario de atencion?")


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"El ID de este chat es: {current_chat_id(update)}")


async def answer_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    chat_id = current_chat_id(update)
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            if not await is_authorized_chat(update, client):
                return

            response = await client.post(
                f"{API_URL}/api/bot/query",
                json={"query": text, "telegram_user": chat_id},
            )
            response.raise_for_status()
            data = response.json()
            await update.message.reply_text(data["answer"])
        except httpx.HTTPError:
            await update.message.reply_text("No pude consultar la API en este momento.")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError("Configura TELEGRAM_BOT_TOKEN en el archivo .env")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer_message))
    application.run_polling()


if __name__ == "__main__":
    main()
