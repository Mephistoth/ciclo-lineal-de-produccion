from email import message
from time import process_time_ns
from django.shortcuts import get_object_or_404, redirect, render
from .models import AreaEmpresa, Entrada, Etapa, RegistroTrabajador, Salida, Oportunidades, Empresa
from django.contrib import messages
from .forms import EntradaForm, SalidaForm, OportunidadForm
from user.models import Usuario
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from django.http import HttpResponse
from io import BytesIO
import base64

# Create your views here.
def home(request):
    # obj_cliente = User.objects.only('rut').get(rut=rut)
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        return render(request, 'home.html', {'registros': registros})
    else:
        return render(request, 'home.html')

def autoDiagnostico(request, empresa_id=None):
    if not request.user.is_authenticated:
        return render(request, 'autodiagnostico/auto_diagnostico.html')

    empresas = Empresa.objects.all()  # para admins
    registros = RegistroTrabajador.objects.filter(usuario=request.user)

    empresa_seleccionada = None
    if empresa_id:
        empresa_seleccionada = Empresa.objects.get(id_empresa=empresa_id)

    contexto = {
        'registros': registros,
        'empresas': empresas,
        'empresa_seleccionada': empresa_seleccionada
    }

    return render(request, 'autodiagnostico/auto_diagnostico.html', contexto)


def extraccionMateriaPrima(request):
    empresa_id = request.GET.get("empresa")
    empresa_seleccionada = None


    if empresa_id:
            empresa_seleccionada = Empresa.objects.get(id_empresa=empresa_id)

    empresas = Empresa.objects.all()

    if request.user.is_authenticated:

        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Extraccion materia prima")
        entradas = Entrada.objects.filter(usuario=request.user)
        # etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(activo=True)
        print("La id de la etapa es!!!!!!!!: ", etapa)

        # data = {

        #     'form' : EntradaForm(),
        #     'registros':registros,
        #     'entradas':entradas,
        #     'formSalida': SalidaForm()

        # }
        print(f"la id del usuario es!!!!!!!!:", request.user.id)
        formulario = EntradaForm()
        formularioSalida = SalidaForm()

        if request.method == 'POST':
            formulario = EntradaForm(request.POST)
            formularioSalida = SalidaForm(request.POST)

            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                formulario = EntradaForm()

            if formularioSalida.is_valid():
                post = formularioSalida.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                formularioSalida.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                formulario = SalidaForm()
        return render(request, 'autodiagnostico/extraccion/home_extraccion.html', {'form': formulario,
         'registros': registros, 'entradas': entradas, 'empresas': empresas, 'empresa_seleccionada': empresa_seleccionada})
    else:
        return render(request, 'autodiagnostico/extraccion/home_extraccion.html')


def agregarEntradaExtraccion(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.filter(nombre="Extraccion materia prima").first()
        areaTrabajador = RegistroTrabajador.objects.filter(usuario=request.user).values_list("id_area", flat=True).first()

        entradas = Entrada.objects.filter(usuario=request.user, etapa=etapa)

        data = {
            'form': EntradaForm(),
            'registros': registros,
            'entradas': entradas,
            'areaTrabajador': areaTrabajador,
        }

        # ======== AGREGAR ENTRADA ========
        if request.method == 'POST':
            formulario = EntradaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.usuario = request.user
                post.etapa = etapa
                post.id_area_id = areaTrabajador
                post.save()
                messages.success(request, "Entrada registrada con éxito.")
                return redirect('agregar_entrada_extraccion')
            else:
                data["form"] = formulario

        return render(request, 'autodiagnostico/extraccion/entrada/agregar_entrada.html', data)

    else:
        return render(request, 'autodiagnostico/extraccion/entrada/agregar_entrada.html')



def eliminarEntradaExtraccion(request, id):
    entrada = get_object_or_404(Entrada, id_entrada=id, usuario=request.user)
    entrada.delete()
    messages.success(request, "Entrada eliminada correctamente.")
    return redirect('agregar_entrada_extraccion')


def agregarSalidaExtraccion(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Extraccion materia prima")
        salidas = Salida.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)

        data = {

            'form': SalidaForm(),
            'registros': registros,
            'salidas': salidas

        }
        print(f"la id del usuario es!!!!!!!!:", request.user.id)

        if request.method == 'POST':
            formulario = SalidaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/extraccion/salida/agregar_salida.html', data)
    else:
        return render(request, 'autodiagnostico/extraccion/entrada/agregar_salida.html')

def eliminarSalidaExtraccion(request, id):
    salida = get_object_or_404(Salida, id_salida=id, usuario=request.user)
    salida.delete()
    messages.success(request, "Salida eliminada correctamente.")
    return redirect('agregar_salida_extraccion')


def agregarOportunidadExtraccion(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Extraccion materia prima")
        oportunidades = Oportunidades.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)

        data = {

            'form': OportunidadForm(),
            'registros': registros,
            'oportunidad': oportunidades

        }

        if request.method == 'POST':
            formulario = OportunidadForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/extraccion/oportunidad/agregar_oportunidad.html', data)
    else:
        return render(request, 'autodiagnostico/extraccion/oportunidad/agregar_oportunidad.html')

def eliminarOportunidadExtraccion(request, id):
    oportunidad = get_object_or_404(Oportunidades, id_oportunidad=id, usuario=request.user)
    oportunidad.delete()
    messages.success(request, "Oportunidad eliminada correctamente.")
    return redirect('agregar_oportunidad_extraccion')




# Diseño y produccion

def diseño_Produccion(request):

    empresa_id = request.GET.get("empresa")
    empresa_seleccionada = None

    if empresa_id:
        empresa_seleccionada = Empresa.objects.filter(id_empresa=empresa_id).first()

    empresas = Empresa.objects.all()

    registros = RegistroTrabajador.objects.filter(usuario=request.user)

    data = {
        'registros': registros,
        'empresas': empresas,
        'empresa_seleccionada': empresa_seleccionada,
        'empresa_id': empresa_id,
    }

    return render(request, 'autodiagnostico/diseñoProduccion/home_diseño.html', data)



def agregarEntradaDiseño(request):
    if request.user.is_authenticated:

        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Diseño y produccion")
        entradas = Entrada.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)
        # etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(activo=True)
        data = {

            'form': EntradaForm(),
            'registros': registros,
            'entradas': entradas

        }
        if request.method == 'POST':
            formulario = EntradaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/diseñoProduccion/entrada/agregar_entrada.html', data)
    else:
        return render(request, 'autodiagnostico/diseñoProduccion/entrada/agregar_entrada.html')


def eliminarEntradaDiseño(request, id):
    entrada = get_object_or_404(Entrada, id_entrada=id, usuario=request.user)
    entrada.delete()
    messages.success(request, "Entrada eliminada correctamente.")
    return redirect('agregar_entrada_diseño')


def agregarSalidaDiseño(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Diseño y produccion")
        salidas = Salida.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)

        data = {

            'form': SalidaForm(),
            'registros': registros,
            'salidas': salidas

        }

        if request.method == 'POST':
            formulario = SalidaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/diseñoProduccion/salida/agregar_salida.html', data)
    else:
        return render(request, 'autodiagnostico/diseñoProduccion/entrada/agregar_salida.html')


def eliminarSalidaDiseño(request, id):
    salida = get_object_or_404(Salida, id_salida=id, usuario=request.user)
    salida.delete()
    messages.success(request, "Salida eliminada correctamente.")
    return redirect('agregar_salida_diseño')


def agregarOportunidadDiseño(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Diseño y produccion")
        oportunidades = Oportunidades.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)

        data = {

            'form': OportunidadForm(),
            'registros': registros,
            'oportunidad': oportunidades

        }

        if request.method == 'POST':
            formulario = OportunidadForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/diseñoProduccion/oportunidad/agregar_oportunidad.html', data)
    else:
        return render(request, 'autodiagnostico/diseñoProduccion/oportunidad/agregar_oportunidad.html')


def eliminarOportunidadDiseño(request, id):
    oportunidad = get_object_or_404(Oportunidades, id_oportunidad=id, usuario=request.user)
    oportunidad.delete()
    messages.success(request, "Oportunidad eliminada correctamente.")
    return redirect('agregar_oportunidad_diseño')



# logistica

def logistica(request):
    empresa_id = request.GET.get("empresa")
    empresa_seleccionada = None

    if empresa_id:
        empresa_seleccionada = Empresa.objects.filter(id_empresa=empresa_id).first()

    empresas = Empresa.objects.all()

    registros = RegistroTrabajador.objects.filter(usuario=request.user)

    data = {  
            'registros': registros, 
            'empresas': empresas,
            'empresa_seleccionada': empresa_seleccionada,
            'empresa_id': empresa_id,
    }

    return render(request,'autodiagnostico/logistica/home_logistica.html', data)


def agregarEntradaLogistica(request):
    if request.user.is_authenticated:

        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Logistica")
        entradas = Entrada.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)
        # etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(activo=True)
        data = {

            'form': EntradaForm(),
            'registros': registros,
            'entradas': entradas

        }
        if request.method == 'POST':
            formulario = EntradaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/logistica/entrada/agregar_entrada.html', data)
    else:
        return render(request, 'autodiagnostico/logistica/entrada/agregar_entrada.html')


def eliminarEntradaLogistica(request, id):
    entrada = get_object_or_404(Entrada, id_entrada=id, usuario=request.user)
    entrada.delete()
    messages.success(request, "Entrada eliminada correctamente.")
    return redirect('agregar_entrada_logistica')


def agregarSalidaLogistica(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Logistica")
        salidas = Salida.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)

        data = {

            'form': SalidaForm(),
            'registros': registros,
            'salidas': salidas

        }

        if request.method == 'POST':
            formulario = SalidaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/logistica/salida/agregar_salida.html', data)
    else:
        return render(request, 'autodiagnostico/logistica/entrada/agregar_salida.html')


def eliminarSalidaLogistica(request, id):
    salida = get_object_or_404(Salida, id_salida=id, usuario=request.user)
    salida.delete()
    messages.success(request, "Salida eliminada correctamente.")
    return redirect('agregar_salida_logistica')



def agregarOportunidadLogistica(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Logistica")
        oportunidades = Oportunidades.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)

        data = {

            'form': OportunidadForm(),
            'registros': registros,
            'oportunidad': oportunidades

        }

        if request.method == 'POST':
            formulario = OportunidadForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/logistica/oportunidad/agregar_oportunidad.html', data)
    else:
        return render(request, 'autodiagnostico/logistica/oportunidad/agregar_oportunidad.html')

def eliminarOportunidadLogistica(request, id):
    oportunidad = get_object_or_404(Oportunidades, id_oportunidad=id, usuario=request.user)
    oportunidad.delete()
    messages.success(request, "Oportunidad eliminada correctamente.")
    return redirect('agregar_oportunidad_logistica')



#compra

def compra(request):
    empresa_id = request.GET.get("empresa")
    empresa_seleccionada = None

    if empresa_id:
        empresa_seleccionada = Empresa.objects.filter(id_empresa=empresa_id).first()

    empresas = Empresa.objects.all()

    registros = RegistroTrabajador.objects.filter(usuario=request.user)

    data = {  
            'registros': registros, 
            'empresas': empresas,
            'empresa_seleccionada': empresa_seleccionada,
            'empresa_id': empresa_id,
    }

    return render(request,'autodiagnostico/compra/home_compra.html', data)


def agregarEntradaCompra(request):
    if request.user.is_authenticated:

        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Compra")
        entradas = Entrada.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)
        # etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(activo=True)
        data = {

            'form': EntradaForm(),
            'registros': registros,
            'entradas': entradas

        }
        if request.method == 'POST':
            formulario = EntradaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/compra/entrada/agregar_entrada.html', data)
    else:
        return render(request, 'autodiagnostico/compra/entrada/agregar_entrada.html')   

def eliminarEntradaCompra(request, id):
    entrada = get_object_or_404(Entrada, id_entrada=id, usuario=request.user)
    entrada.delete()
    messages.success(request, "Entrada eliminada correctamente.")
    return redirect('agregar_entrada_compra')


def agregarSalidaCompra(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Compra")
        salidas = Salida.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)

        data = {

            'form': SalidaForm(),
            'registros': registros,
            'salidas': salidas

        }

        if request.method == 'POST':
            formulario = SalidaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/compra/salida/agregar_salida.html', data)
    else:
        return render(request,'autodiagnostico/compra/salida/agregar_salida.html')  


def eliminarSalidaCompra(request, id):
    salida = get_object_or_404(Salida, id_salida=id, usuario=request.user)
    salida.delete()
    messages.success(request, "Salida eliminada correctamente.")
    return redirect('agregar_salida_compra')



def agregarOportunidadCompra(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Compra")
        oportunidades = Oportunidades.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)

        data = {

            'form': OportunidadForm(),
            'registros': registros,
            'oportunidad': oportunidades

        }

        if request.method == 'POST':
            formulario = OportunidadForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/compra/oportunidad/agregar_oportunidad.html', data)
    else:
        return render(request, 'autodiagnostico/compra/oportunidad/agregar_oportunidad.html') 

def eliminarOportunidadCompra(request, id):
    oportunidad = get_object_or_404(Oportunidades, id_oportunidad=id, usuario=request.user)
    oportunidad.delete()
    messages.success(request, "Oportunidad eliminada correctamente.")
    return redirect('agregar_oportunidad_compra')



#Uso consumo

def usoConsumo(request):
    empresa_id = request.GET.get("empresa")
    empresa_seleccionada = None

    if empresa_id:
        empresa_seleccionada = Empresa.objects.filter(id_empresa=empresa_id).first()

    empresas = Empresa.objects.all()

    registros = RegistroTrabajador.objects.filter(usuario=request.user)

    data = {  
            'registros': registros, 
            'empresas': empresas,
            'empresa_seleccionada': empresa_seleccionada,
            'empresa_id': empresa_id,
    }

    return render(request,'autodiagnostico/usoConsumo/home_usoConsumo.html', data)        


def agregarEntradaUso(request):
    if request.user.is_authenticated:

        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Uso consumo")
        entradas = Entrada.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)
        # etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(activo=True)
        data = {

            'form': EntradaForm(),
            'registros': registros,
            'entradas': entradas

        }
        if request.method == 'POST':
            formulario = EntradaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/usoConsumo/entrada/agregar_entrada.html', data)
    else:
        return render(request, 'autodiagnostico/usoConsumo/entrada/agregar_entrada.html')    


def eliminarEntradaUsoConsumo(request, id):
    entrada = get_object_or_404(Entrada, id_entrada=id, usuario=request.user)
    entrada.delete()
    messages.success(request, "Entrada eliminada correctamente.")
    return redirect('agregar_entrada_uso_consumo')


def agregarSalidaUso(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Uso consumo")
        salidas = Salida.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)

        data = {

            'form': SalidaForm(),
            'registros': registros,
            'salidas': salidas

        }

        if request.method == 'POST':
            formulario = SalidaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/usoConsumo/salida/agregar_salida.html', data)
    else:
        return render(request,'autodiagnostico/usoConsumo/salida/agregar_salida.html')       


def eliminarSalidaUso(request, id):
    salida = get_object_or_404(Salida, id_salida=id, usuario=request.user)
    salida.delete()
    messages.success(request, "Salida eliminada correctamente.")
    return redirect('agregar_salida_uso')



def agregarOportunidadUso(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Uso consumo")
        oportunidades = Oportunidades.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)

        data = {

            'form': OportunidadForm(),
            'registros': registros,
            'oportunidad': oportunidades

        }

        if request.method == 'POST':
            formulario = OportunidadForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/usoConsumo/oportunidad/agregar_oportunidad.html', data)
    else:
        return render(request, 'autodiagnostico/usoConsumo/oportunidad/agregar_oportunidad.html')   

def eliminarOportunidadUso(request, id):
    oportunidad = get_object_or_404(Oportunidades, id_oportunidad=id, usuario=request.user)
    oportunidad.delete()
    messages.success(request, "Oportunidad eliminada correctamente.")
    return redirect('agregar_oportunidad_uso')


# Fin de vida

def finVida(request):
    empresa_id = request.GET.get("empresa")
    empresa_seleccionada = None

    if empresa_id:
        empresa_seleccionada = Empresa.objects.filter(id_empresa=empresa_id).first()

    empresas = Empresa.objects.all()

    registros = RegistroTrabajador.objects.filter(usuario=request.user)

    data = {  
            'registros': registros, 
            'empresas': empresas,
            'empresa_seleccionada': empresa_seleccionada,
            'empresa_id': empresa_id,
    }

    return render(request,'autodiagnostico/finVida/home_finVida.html', data)


def agregarEntradaFin(request):
    if request.user.is_authenticated:

        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Fin de vida")
        entradas = Entrada.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)
        # etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(activo=True)
        data = {

            'form': EntradaForm(),
            'registros': registros,
            'entradas': entradas

        }
        if request.method == 'POST':
            formulario = EntradaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Entrada Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/finVida/entrada/agregar_entrada.html', data)
    else:
        return render(request, 'autodiagnostico/finVida/entrada/agregar_entrada.html')  


def eliminarEntradaFinVida(request, id):
    entrada = get_object_or_404(Entrada, id_entrada=id, usuario=request.user)
    entrada.delete()
    messages.success(request, "Entrada eliminada correctamente.")
    return redirect('agregar_entrada_fin_vida')


def agregarSalidaFin(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Fin de vida")
        salidas = Salida.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)

        data = {

            'form': SalidaForm(),
            'registros': registros,
            'salidas': salidas

        }

        if request.method == 'POST':
            formulario = SalidaForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/finVida/salida/agregar_salida.html', data)
    else:
        return render(request,'autodiagnostico/finVida/salida/agregar_salida.html') 


def eliminarSalidaFinVida(request, id):
    salida = get_object_or_404(Salida, id_salida=id, usuario=request.user)
    salida.delete()
    messages.success(request, "Salida eliminada correctamente.")
    return redirect('agregar_salida_fin_vida')



def agregarOportunidadFin(request):
    if request.user.is_authenticated:
        registros = RegistroTrabajador.objects.filter(usuario=request.user)
        etapa = Etapa.objects.values_list("id_etapa", flat=True).filter(nombre="Fin de vida")
        oportunidades = Oportunidades.objects.filter(usuario=request.user)
        areaTrabajador = RegistroTrabajador.objects.values_list("id_area", flat=True).filter(usuario = request.user)

        data = {

            'form': OportunidadForm(),
            'registros': registros,
            'oportunidad': oportunidades

        }

        if request.method == 'POST':
            formulario = OportunidadForm(data=request.POST, files=request.FILES)
            if formulario.is_valid():
                post = formulario.save(commit=False)
                post.nombre = request.POST["nombre"]
                post.usuario_id = request.user.id
                post.etapa_id = etapa
                post.id_area_id = areaTrabajador
                formulario.save()
                messages.success(request, "Salida Registrada con exito")
            else:
                data["form"] = formulario
        return render(request,'autodiagnostico/finVida/oportunidad/agregar_oportunidad.html', data)
    else:
        return render(request, 'autodiagnostico/finVida/oportunidad/agregar_oportunidad.html') 

def eliminarOportunidadFinVida(request, id):
    oportunidad = get_object_or_404(Oportunidades, id_oportunidad=id, usuario=request.user)
    oportunidad.delete()
    messages.success(request, "Oportunidad eliminada correctamente.")
    return redirect('agregar_oportunidad_fin_vida')