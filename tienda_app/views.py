
from .infra.gateways import BancoNacionalProcesador
from .services import CompraService, CompraRapidaService

import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import View

from .models import Libro, Inventario, Orden
from .infra.factories import PaymentFactory


# 1. Vista original del profesor
class CompraView(View):
    """
    CBV: Vista Basada en Clases.
    Actúa como un "Portero": recibe la petición
    y delega al servicio.
    """

    template_name = 'tienda_app/compra.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)

        return render(
            request,
            self.template_name,
            contexto
        )

    def post(self, request, libro_id):
        servicio = self.setup_service()

        try:
            total = servicio.ejecutar_compra(
                libro_id,
                cantidad=1
            )

            return render(
                request,
                self.template_name,
                {
                    'mensaje_exito': (
                        f"¡Gracias por su compra! Total: ${total}"
                    ),
                    'total': total,
                },
            )

        except (ValueError, Exception) as e:
            return render(
                request,
                self.template_name,
                {'error': str(e)},
                status=400
            )


# 2. Primera versión: Function-Based View (Spaghetti)
def compra_rapida_fbv(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if request.method == 'POST':
        # SRP: Lógica de inventario dentro de la vista
        inventario = Inventario.objects.get(libro=libro)

        if inventario.cantidad > 0:
            # OCP: Cálculo del impuesto directamente
            total = float(libro.precio) * 1.19

            # DIP: Pago acoplado a un archivo local
            with open("pagos_manuales.log", "a") as f:
                f.write(
                    f"[{datetime.datetime.now()}] "
                    f"Pago FBV: ${total}\n"
                )

            inventario.cantidad -= 1
            inventario.save()

            Orden.objects.create(
                libro=libro,
                total=total
            )

            return HttpResponse(
                f"Compra exitosa: {libro.titulo}"
            )

        return HttpResponse("Sin stock", status=400)

    total_estimado = float(libro.precio) * 1.19

    return render(
        request,
        'tienda_app/compra_rapida.html',
        {
            'libro': libro,
            'total': total_estimado
        }
    )


# 3. Versión mejorada: CBV + Service Layer

class CompraRapidaView(View):
    template_name = 'tienda_app/compra_rapida.html'

    def get(self, request, libro_id):
        servicio = CompraService(BancoNacionalProcesador())
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = CompraRapidaService(BancoNacionalProcesador())
        try:
            total = servicio.procesar(libro_id)
            if total is None:
                return HttpResponse("Pago rechazado", status=400)
            return HttpResponse(f"Compra exitosa. Total: ${total}")
        except ValueError as error:
            return HttpResponse(str(error), status=400)
