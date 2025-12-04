import os
import sys
import django

# ==========================================
# CONFIGURAR DJANGO
# ==========================================

# Ruta al proyecto (carpeta donde está manage.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cicloProduccion.settings")

django.setup()

# ==========================================
# IMPORTAR MODELOS
# ==========================================

from django.conf import settings
from django.core.mail import send_mail
from app.models import AreaEmpresa, RegistroTrabajador
from app.models import Entrada, Salida, Oportunidades
from user.models import Usuario


# ==========================================
# LÓGICA — OBTENER USUARIOS
# ==========================================

def obtener_usuarios_sin_actividad(id_empresa):

    areas_ids = AreaEmpresa.objects.filter(
        id_empresa=id_empresa
    ).values_list('id_area', flat=True)

    usuarios_ids = RegistroTrabajador.objects.filter(
        id_area__in=areas_ids
    ).values_list("usuario_id", flat=True)

    usuarios_sin_act = Usuario.objects.filter(id__in=usuarios_ids) \
        .exclude(id__in=Entrada.objects.values_list("usuario_id", flat=True)) \
        .exclude(id__in=Salida.objects.values_list("usuario_id", flat=True)) \
        .exclude(id__in=Oportunidades.objects.values_list("usuario_id", flat=True))

    return usuarios_sin_act


# ==========================================
# ENVÍO DE RECORDATORIOS
# ==========================================

def enviar_recordatorios_panaderia():
    ID_PANADERIA = 1

    print("Buscando usuarios sin actividad...")

    usuarios = obtener_usuarios_sin_actividad(ID_PANADERIA)

    if not usuarios.exists():
        print("No hay usuarios faltantes en PANADERIA.")
        return

    enviados = 0

    for u in usuarios:
        if not u.email:
            continue

        try:
            send_mail(
                subject="Recordatorio — Lineal a Circular",
                message=(
                    f"Hola {u.first_name or u.username},\n\n"
                    "Te recordamos completar tus respuestas de Entradas, "
                    "Salidas y Oportunidades.\n\n"
                    "Gracias,\nEquipo Ciclo Circular."
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[u.email],
                fail_silently=False,
            )
            enviados += 1
        except Exception as e:
            print(f"Error enviando a {u.email}: {e}")

    print(f"Emails enviados correctamente: {enviados}")


if __name__ == "__main__":
    enviar_recordatorios_panaderia()