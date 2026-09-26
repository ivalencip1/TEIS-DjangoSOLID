
from django.urls import path
from .api.views import CompraAPIView
from .views import CompraView, compra_rapida_fbv, CompraRapidaView

urlpatterns = [
    # Vista original del profesor
    path(
        'compra/<int:libro_id>/',
        CompraView.as_view(),
        name='finalizar_compra'
    ),

    # Nuestra vista basada en funciones (FBV)
    path(
        'compra-rapida/<int:libro_id>/',
        compra_rapida_fbv,
        name='compra_rapida'
    ),

    # API original
    path(
        'api/v1/comprar/',
        CompraAPIView.as_view(),
        name='api_comprar'
    ),

    # Nuestra nueva vista basada en clases (CBV)
    path(
        'compra-rapida-cbv/<int:libro_id>/',
        CompraRapidaView.as_view(),
        name='compra_rapida_cbv'
    ),
]
