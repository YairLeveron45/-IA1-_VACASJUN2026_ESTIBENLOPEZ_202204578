function TelegramForm({
  notifyTelegram,
  onToggle,
}) {
  return (
    <section className="panel">
      <h2>Telegram</h2>

      <p>
        Activa esta opción para enviar automáticamente el diagnóstico al bot de
        Telegram configurado en el backend.
      </p>

      <label className="toggle-row">
        <input
          type="checkbox"
          checked={notifyTelegram}
          onChange={(event) => onToggle(event.target.checked)}
        />

        <span>Enviar diagnóstico a Telegram</span>
      </label>
    </section>
  );
}

export default TelegramForm;