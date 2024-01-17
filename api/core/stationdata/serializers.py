from rest_framework import serializers
from core.user.models import User

from rest_framework import serializers
from .models import *

# Empresa Serializer
class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'
# Station Serializer
class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estacion
        fields = '__all__'
# Producto Serializer
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'  
# Tanque Serializer
class TanqueSerializer(serializers.ModelSerializer):
    station = StationSerializer(read_only=True)
    producto = ProductoSerializer(read_only=True)
    station_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Estacion.objects.all(), source='station'
    )
    producto_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Producto.objects.all(), source='producto'
    )

    class Meta:
        model = Tanque
        fields = '__all__'  
        
# Dispensario Serializer
class DispensarioSerializer(serializers.ModelSerializer):
    station = StationSerializer(read_only=True)
    station_id = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Estacion.objects.all(), source='station'
    )

    class Meta:
        model = Dispensario
        fields = '__all__'  




# Compras Serializer
class ComprasSerializer(serializers.ModelSerializer):
    Estacion = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Estacion.objects.all()
    )
    Producto = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Producto.objects.all()
    )

    class Meta:
        model = Compras
        fields = ['compra_id', 'Estacion', 'Producto', 'volumen', 'Fecha']

class VentasSerializer(serializers.ModelSerializer):
    Estacion = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Estacion.objects.all()
    )
    Producto = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Producto.objects.all() 
    )

    class Meta:
        model = Ventas
        fields = ['Venta_id', 'Estacion', 'Producto', 'volumen', 'Fecha']

# PruebaBombas Serializer
class PruebaBombasSerializer(serializers.ModelSerializer):
    Estacion = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Estacion.objects.all() 
    )
    Producto = serializers.PrimaryKeyRelatedField(
        write_only=True, queryset=Producto.objects.all()
    )

    class Meta:
        model = PruebaBombas
        fields = ['Prueba_id', 'Estacion', 'Producto', 'volumen', 'Fecha']



class SimpleAutoTanqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoTanque
        fields = ('Unidad_id', 'Nombre')
        
# CargaAutotanques Serializer
class CargaAutotanquesSerializer(serializers.ModelSerializer):
    station = StationSerializer(read_only=True)

    class Meta:
        model = CargaAutoTanques
        fields = '__all__'

# ReporteDinero Serializer
class ReporteDineroSerializer(serializers.ModelSerializer):
    station = StationSerializer(read_only=True)

    class Meta:
        model = ReporteDinero
        fields = '__all__'

class AutotanqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoTanque
        fields = '__all__'  

class CATTABCUBSerializer(serializers.ModelSerializer):
    class Meta:
        model = CATTABCUB
        fields = '__all__'  

class MOVMEDTANQerializer(serializers.ModelSerializer):
    class Meta:
        model = MOVMEDTANQ
        fields = '__all__'  


