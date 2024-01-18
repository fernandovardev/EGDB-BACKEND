from rest_framework import viewsets, filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from core.stationdata.models import *
from core.stationdata.serializers import *
from datetime import datetime, timedelta
from django.utils.timezone import now
import csv
import io
from django.http import HttpResponse



class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['razon_social']

class StationViewSet(viewsets.ModelViewSet):
    queryset = Estacion.objects.all()
    serializer_class = StationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['estacion_id']

    @action(detail=False, methods=['get'])
    def station_list(self, request, pk=None):
        """
        Enlist station by name.
        """
        try:
            # Query the database for stations
            stations = Estacion.objects.filter(
                Q(is_WHOLESALE=True) | Q(Estacion_id='004')
            ).exclude(
                Estacion_id__in=['001', '008']
            ).values('Estacion_id', 'Estacion_Nombre')            
            stations = [
                    {'estacion_id': station['Estacion_id'], 'estacion_nombre': station['Estacion_Nombre']}
                    for station in stations
                ]
            return Response(stations)
        except Estacion.DoesNotExist:
            return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['get'])
    def is_wholesale(self, request, pk=None):
        """
        Check if the given station is wholesale or not.
        """
        try:
            station = self.get_object()
            is_wholesale = station.is_WHOLESALE
            return Response({'is_wholesale': is_wholesale}, status=status.HTTP_200_OK)
        except Estacion.DoesNotExist:
            return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)
    @action(detail=False, methods=['get'])
    def super_stations(self, request):
        """
        Retrieve a list of estacion_id where IS_SUPER is true.
        """
        super_stations = Estacion.objects.filter(is_SUPER=True).values_list('Estacion_id', flat=True)
        return Response({'super_stations': list(super_stations)})
    @action(detail=False, methods=['get'])
    def product_order(self, request):
        """
        Retrieve a mapping of station IDs to unique arrays of product IDs.
        """
        tanques = Tanque.objects.values('Estacion__Estacion_id', 'Producto__Producto_id').distinct()
        product_order = {}
        for tanque in tanques:
            estacion_id = tanque['Estacion__Estacion_id']
            producto_id = tanque['Producto__Producto_id']
            if estacion_id not in product_order:
                product_order[estacion_id] = set()
            product_order[estacion_id].add(producto_id)

        # Convert sets to lists
        for estacion_id in product_order:
            product_order[estacion_id] = list(product_order[estacion_id])

        return Response(product_order)

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre']

class TanqueViewSet(viewsets.ModelViewSet):
    queryset = Tanque.objects.all()
    serializer_class = TanqueSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'numero']

class DispensarioViewSet(viewsets.ModelViewSet):
    queryset = Dispensario.objects.all()
    serializer_class = DispensarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nombre', 'codigo']

class CargaAutoTanquesViewset(viewsets.ModelViewSet):
    queryset = CargaAutoTanques.objects.all()
    serializer_class = CargaAutotanquesSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
        
class ComprasViewSet(viewsets.ModelViewSet):
    queryset = Compras.objects.all()
    serializer_class = ComprasSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['fecha', 'volumen']

class VentasViewSet(viewsets.ModelViewSet):
    queryset = Ventas.objects.all()
    serializer_class = VentasSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['Fecha', 'volumen']

class PruebaBombasViewSet(viewsets.ModelViewSet):
    queryset = PruebaBombas.objects.all()
    serializer_class = PruebaBombasSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['Fecha', 'volumen']

class ComprasViewSet(viewsets.ModelViewSet):
    queryset = Compras.objects.all()
    serializer_class = ComprasSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['Fecha', 'volumen']

class AutotanqueViewSet(viewsets.ModelViewSet):
    queryset = AutoTanque.objects.all()
    serializer_class = AutotanqueSerializer  # Default serializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['unidad_id', 'kilometraje_act']

    def get_serializer_class(self):
        if self.action == 'list':
            return SimpleAutoTanqueSerializer
        return super().get_serializer_class()
    
class ReporteDineroViewSet(viewsets.ModelViewSet):
    queryset = ReporteDinero.objects.all()
    serializer_class = ReporteDineroSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['fecha', 'importe']

class MOVMEDTANQViewSet(viewsets.ModelViewSet):
    queryset = MOVMEDTANQ.objects.all()
    serializer_class = MOVMEDTANQerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['fecha', 'importe']

    @action(detail=False, methods=['get'])
    def latest_fecha(self, request, *args, **kwargs):
        estacion_id = request.query_params.get('estacion_id')
        if not estacion_id:
            return Response({"error": "Estacion ID is required"}, status=400)

        latest_record = MOVMEDTANQ.objects.filter(ESTACION_id=estacion_id).order_by('-FECHA').first()
        if latest_record:
            return Response({"latest_fecha": latest_record.FECHA})
        else:
            # Get the last day of the previous month
            today = datetime.today()
            first_day_of_current_month = datetime(today.year, today.month, 1)
            last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
            return Response({"message": "No records found for the given station", 
                            "last_day_previous_month": last_day_of_previous_month.date()})
    @action(detail=False, methods=['get'])
    def fetch_by_station_and_date(self, request, *args, **kwargs):
        estacion_id = request.query_params.get('estacion_id')
        fecha = request.query_params.get('fecha')

        if not estacion_id or not fecha:
            return Response({"error": "Both Estacion ID and Fecha are required"}, status=400)

        try:
            records = MOVMEDTANQ.objects.filter(ESTACION_id=estacion_id, FECHA=fecha)
            if records.exists():
                serializer = self.get_serializer(records, many=True)
                return Response(serializer.data)
            else:
                return Response({"message": "No records found for the given station and date"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        
    @action(detail=False, methods=['put'])
    def update_records(self, request, *args, **kwargs):
        data = request.data
        estacion_id = data.get('station')
        fecha = data.get('date')
        tanks_data = data.get('tanks', [])

        if not estacion_id or not fecha:
            return Response({"error": "Estacion ID and Fecha are required"}, status=400)

        try:
            for tank in tanks_data:
                tank_id = tank.get('TANQUE_ID')  # Extract TANQUE_ID from each tank record
                record, created = MOVMEDTANQ.objects.update_or_create(
                    ESTACION_id=estacion_id, TANQUE_ID=tank_id, FECHA=fecha,
                    defaults={
                        'CMSREG': tank.get('CMSREG'),
                        'LTSREG': tank.get('LTSREG'),
                        'LTSETT': tank.get('LTSETT')
                    }
                )
                # Additional processing as needed
            return Response({"message": "Records updated successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
    @action(detail=False, methods=['get'])
    def delete_by_station(self, request, *args, **kwargs):
        estacion_id = request.query_params.get('estacion_id')

        if not estacion_id:
            return Response({"error": "Estacion ID is required"}, status=400)

        MOVMEDTANQ.objects.filter(ESTACION_id=estacion_id).delete()
        return Response({"message": f"All records for ESTACION_id {estacion_id} have been deleted successfully"}, status=200)

class movmedagualuzViewSet(viewsets.ModelViewSet):
    queryset = movmedagualuz.objects.all()
    serializer_class = movmedagualuzSerializer

    # Method to fetch records by date and station
    @action(detail=False, methods=['get'])
    def get_medluzact_medaguaact_by_fecha(self, request):
        fecha = request.query_params.get('FECHA')
        estacion_id = request.query_params.get('ESTACION')
        if fecha and estacion_id:
            queryset = movmedagualuz.objects.filter(FECHA=fecha, ESTACION=estacion_id).values('MEDLuzAct', 'MEDAguaAct')
            if queryset.exists():
                return Response(queryset)
            else:
                return Response([{'MEDLuzAct': 0, 'MEDAguaAct': 0}])
        else:
            return Response({"error": "Both FECHA and ESTACION parameters are required"}, status=status.HTTP_400_BAD_REQUEST)
    # Method to update records
    @action(detail=True, methods=['put'])
    def update_records(self, request, pk=None):
        # Update logic here
        # Use the 'pk' if you want to update a specific record
        # You can use the movmedagualuzSerializer for serialization/deserialization
        return Response({"message": "Update functionality not implemented yet"}, status=status.HTTP_501_NOT_IMPLEMENTED)

    # Method to delete records by station
    @action(detail=True, methods=['delete'])
    def delete_by_station(self, request, pk=None):
        # Delete logic here
        # Use the 'pk' as the station ID for deletion
        return Response({"message": "Delete functionality not implemented yet"}, status=status.HTTP_501_NOT_IMPLEMENTED)