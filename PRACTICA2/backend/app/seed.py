import os

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from .auth import hash_password
from .models import AdminUser, Category, FAQ, Setting

ADMIN_USERNAME = "IA1-User"
ADMIN_PASSWORD = "IA1-password@_new"

load_dotenv()


def seed_database(db: Session) -> None:
    if not db.query(AdminUser).filter_by(username=ADMIN_USERNAME).first():
        db.add(AdminUser(username=ADMIN_USERNAME, password_hash=hash_password(ADMIN_PASSWORD)))

    categories_data = [
        ("Horarios", "Consultas sobre horarios de atencion y clases."),
        ("Tramites", "Informacion sobre procesos y requisitos."),
        ("Soporte", "Ayuda tecnica y contacto."),
    ]

    categories = {}
    for name, description in categories_data:
        category = db.query(Category).filter_by(name=name).first()
        if not category:
            category = Category(name=name, description=description)
            db.add(category)
            db.flush()
        categories[name] = category

    if db.query(FAQ).count() == 0:
        faqs = [
            (
                "Cual es el horario de atencion?",
                "El horario general de atencion es de lunes a viernes de 8:00 a 17:00. En dias festivos o actividades especiales, el horario puede variar y se recomienda revisar los avisos oficiales.",
                "Horarios",
            ),
            (
                "Hay atencion los sabados?",
                "La atencion los sabados depende de la unidad o area que necesites visitar. Si existe atencion sabatina, normalmente se publica en los canales oficiales con el horario correspondiente.",
                "Horarios",
            ),
            (
                "A que hora inicia la jornada matutina?",
                "La jornada matutina inicia normalmente a las 7:00. Es recomendable presentarse con anticipacion si necesitas realizar algun tramite antes del inicio de clases o actividades.",
                "Horarios",
            ),
            (
                "A que hora finaliza la jornada vespertina?",
                "La jornada vespertina finaliza normalmente a las 21:00. Algunos cursos, laboratorios o actividades administrativas pueden terminar antes segun la programacion establecida.",
                "Horarios",
            ),
            (
                "Donde consulto mi horario de clases?",
                "Puedes consultar tu horario de clases en el portal academico correspondiente. Ingresa con tu usuario institucional y revisa la seccion de asignaciones, cursos o calendario academico.",
                "Horarios",
            ),
            (
                "Cuando publican notas?",
                "Las notas se publican segun el calendario definido por cada curso. Si ya finalizo una evaluacion y la nota no aparece, consulta primero con el docente o auxiliar encargado.",
                "Horarios",
            ),
            (
                "Donde veo fechas importantes?",
                "Las fechas importantes se publican en el calendario academico oficial. Alli puedes revisar periodos de inscripcion, asignaciones, evaluaciones, retiros, vacaciones y cierre de actividades.",
                "Horarios",
            ),
            (
                "Como solicito una constancia?",
                "Para solicitar una constancia debes ingresar al portal academico o comunicarte con el area administrativa correspondiente. Selecciona el tipo de constancia, completa los datos solicitados y verifica si aplica algun pago.",
                "Tramites",
            ),
            (
                "Que requisitos necesito para inscripcion?",
                "Los requisitos de inscripcion pueden variar segun el proceso. Generalmente se solicita documento de identificacion, constancias academicas, comprobantes de pago y completar el formulario oficial.",
                "Tramites",
            ),
            (
                "Como recupero mi usuario?",
                "Para recuperar tu usuario, utiliza la opcion de recuperacion del portal academico. Si no tienes acceso al correo registrado, debes comunicarte con soporte o con el area administrativa.",
                "Tramites",
            ),
            (
                "Como actualizo mis datos?",
                "Para actualizar tus datos personales, ingresa al portal academico y revisa la seccion de perfil o datos del estudiante. Si algun campo esta bloqueado, solicita apoyo al area administrativa.",
                "Tramites",
            ),
            (
                "Donde pago una solvencia?",
                "Los pagos de solvencias se realizan por los medios autorizados por la institucion. Revisa el portal o los canales oficiales para confirmar banco, boleta, concepto de pago y fecha limite.",
                "Tramites",
            ),
            (
                "Como cambio mi correo?",
                "Para cambiar tu correo registrado debes solicitar la actualizacion al area administrativa o desde el portal si la opcion esta disponible. Verifica que el nuevo correo este activo antes de registrarlo.",
                "Tramites",
            ),
            (
                "Como contacto a soporte?",
                "Puedes contactar a soporte por medio del correo institucional, mesa de ayuda o canales oficiales publicados. Incluye tu nombre, usuario, descripcion del problema y capturas si aplica.",
                "Soporte",
            ),
            (
                "Olvide mi contrasena, que hago?",
                "Si olvidaste tu contrasena, utiliza la opcion de recuperacion en el portal. Si el enlace no llega a tu correo, revisa spam o solicita apoyo a soporte con tus datos de identificacion.",
                "Soporte",
            ),
            (
                "El sistema no carga, que puedo hacer?",
                "Si el sistema no carga, verifica tu conexion a internet, actualiza la pagina, limpia la cache del navegador e intenta nuevamente. Si el problema continua, reportalo a soporte.",
                "Soporte",
            ),
            (
                "Puedo usar el sistema desde celular?",
                "Si, puedes usar el sistema desde un navegador movil actualizado. Para una mejor experiencia, se recomienda utilizar Chrome, Firefox o Edge y mantener una conexion estable.",
                "Soporte",
            ),
            (
                "Como reporto un error?",
                "Para reportar un error, envia una descripcion clara del problema, los pasos para reproducirlo, captura de pantalla, fecha, hora aproximada y tu usuario al area de soporte.",
                "Soporte",
            ),
            (
                "Que navegador recomiendan?",
                "Se recomienda utilizar Google Chrome, Mozilla Firefox o Microsoft Edge en sus versiones actualizadas. Evita navegadores desactualizados porque pueden presentar errores de compatibilidad.",
                "Soporte",
            ),
            (
                "Como se usa SmartBot?",
                "Para usar SmartBot, escribe una pregunta desde el chat o grupo autorizado de Telegram. El bot consultara la API REST, buscara una respuesta en la base de datos y respondera automaticamente.",
                "Soporte",
            ),
        ]
        for question, answer, category_name in faqs:
            db.add(FAQ(question=question, answer=answer, category_id=categories[category_name].id))

    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    setting = db.query(Setting).first()
    if not setting:
        db.add(Setting(telegram_chat_id=telegram_chat_id))
    elif telegram_chat_id and not setting.telegram_chat_id:
        setting.telegram_chat_id = telegram_chat_id

    db.commit()
