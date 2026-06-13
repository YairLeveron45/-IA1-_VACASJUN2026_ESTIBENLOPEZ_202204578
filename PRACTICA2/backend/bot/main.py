import os

import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

API_URL = os.getenv("API_URL", "http://web:8000")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hola, soy SmartBot. Escribe una pregunta y buscare una respuesta.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Puedes escribirme consultas como: Cual es el horario de atencion?")


async def answer_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text or ""
    user = update.effective_user.username or str(update.effective_user.id)
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.post(
                f"{API_URL}/api/bot/query",
                json={"query": text, "telegram_user": user},
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
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer_message))
    application.run_polling()


if __name__ == "__main__":
    main()
