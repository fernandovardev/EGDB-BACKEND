from rest_framework import routers
from core.user.viewsets import *
from core.auth.viewsets import RegisterViewSet, LoginViewSet, RefreshViewSet
from core.stationdata.viewsets import *
from core.gasdata.viewset import *

router = routers.SimpleRouter()

# ##################################################################### #
# ################### AUTH                       ###################### #
# ##################################################################### #

router.register(r'auth/register', RegisterViewSet, basename='auth-register')
router.register(r'auth/login', LoginViewSet, basename='auth-login')
router.register(r'auth/refresh', RefreshViewSet, basename='auth-refresh')


# ##################################################################### #
# ################### USER                       ###################### #
# ##################################################################### #

router.register(r'user', UserViewSet, basename='user')
router.register(r'permissions', PermissionViewSet, basename='permissions')
router.register(r'user-permission-assignment', UserPermissionAssignmentViewSet, basename='user-permission-assignment')
# ##################################################################### #
# ################### STATIONDATA                ###################### #
# ##################################################################### #

router.register(r'stationdata/reportes', ReportViewSet, basename='reporte-gen')
router.register(r'stationdata/medidas', RegistroMedidasViewSet, basename='medidas-gen')
router.register(r'compras', ComprasViewSet, basename='compras-gen')
router.register(r'ventas', VentasViewSet, basename='ventas-gen')
router.register(r'pruebabombas', PruebaBombasViewSet,basename='pruebas-gen')
router.register(r'autotanques', AutotanqueViewSet,basename='pruebas-gen')
router.register(r'cargaautotanques', CargaAutoTanquesViewset,basename='cargas-gen')
router.register(r'movmedtanq', MOVMEDTANQViewSet,basename='cargas-gen') 
router.register(r'stationdata/data', UpdateDataViewSet,basename='data-gen')
router.register(r'stationdata/stationinfo', StationViewSet,basename='data-gen')
router.register(r'products', ProductoViewSet,basename='data-gen')
router.register(r'agualuz', movmedagualuzViewSet,basename='data-gen')

urlpatterns = [
    *router.urls,
]