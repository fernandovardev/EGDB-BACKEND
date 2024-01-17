from django.db import models

#MODELO BASE

class BaseModel(models.Model):
    STATUS= models.CharField(max_length=1, default='A')
    FECHAMOV=models.DateField(auto_now_add=True)
    class Meta:
        abstract=True # Set this model as Abstract

# Modelo para Empresa
class Empresa(BaseModel):
    Empresa_id = models.CharField(max_length=2, primary_key=True)
    Razon_social = models.CharField(max_length=40)


# Modelo para Estacion
class Estacion(BaseModel):
    Estacion_id = models.CharField(max_length=3, primary_key=True)
    Empresa= models.ForeignKey(Empresa, on_delete=models.CASCADE)
    is_WHOLESALE = models.BooleanField()
    is_SUPER = models.BooleanField()
    Estacion_Nombre = models.CharField(max_length=20)



# Modelo para Producto
class Producto(BaseModel):
    Producto_id = models.CharField(max_length=4, primary_key=True)
    Nombre = models.CharField(max_length=30)


# Modelo para Tanque
class Tanque(BaseModel):
    tanque_id = models.CharField(max_length=30, primary_key=True)
    Estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    Numero = models.CharField(max_length=20)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    Vertical=  models.CharField(max_length=1)
    Capacidad= models.FloatField(default=0)
    Altura = models.FloatField(default=0)
    Diametro = models.FloatField(default=0)
    Existencia = models.FloatField()
    Usuario_ultmodif = models.CharField(max_length=20)
    class Meta:
        unique_together = (('tanque_id', 'Estacion'),)


# Modelo para Dispensario
class Dispensario(BaseModel):
    Dispensario_id = models.CharField(max_length=3, primary_key=True)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    Estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    NumeroTanque = models.CharField(max_length=2)
    codigo = models.CharField(max_length=5)
    Nombre = models.CharField(max_length=40)


# Modelo para ReporteDinero
class ReporteDinero(BaseModel):
    Reporte_dinero_id = models.AutoField(primary_key=True)
    Estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    Fecha = models.DateField()
    PANAMERICANO =  models.FloatField()
    SUPER = models.FloatField()
   


# Modelo para AutoTanque
class AutoTanque(BaseModel):
    Unidad_id = models.CharField(max_length=2, primary_key=True)
    Nombre = models.CharField(max_length=40)
    Empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    kilometraje_act = models.FloatField()
    ultima_modif = models.DateField()

# Modelo para CargaAutoTanques
class CargaAutoTanques(BaseModel):
    Carga_id = models.AutoField(primary_key=True)
    Estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    Unidad = models.ForeignKey(AutoTanque, on_delete=models.CASCADE)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    volumen_Carga = models.FloatField()
    kilometraje = models.FloatField()
    Fecha = models.DateField()



# Modelo para Compras
class Compras(BaseModel):
    compra_id = models.AutoField(primary_key=True)
    Estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    volumen = models.FloatField()
    Fecha= models.DateField()

# Modelo para Ventas
class Ventas(BaseModel):
    Venta_id = models.AutoField(primary_key=True)
    Estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    volumen = models.FloatField()
    Fecha = models.DateField()

# Modelo para PruebaBombas
class PruebaBombas(BaseModel):
    Prueba_id = models.AutoField(primary_key=True)
    Estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    Producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    volumen = models.FloatField()
    Fecha = models.DateField()

class CATTABCUB(models.Model):
    ESTACION = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    TANQUE_ID =  models.CharField(max_length=2)
    CMS =  models.CharField(max_length=4)
    LITROS =  models.DecimalField(max_digits=15, decimal_places=2)
    STATUS= models.CharField(max_length=1, default='A')

class MOVMEDTANQ(BaseModel):
    FECHA = models.DateField()
    ESTACION = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    TANQUE_ID =  models.CharField(max_length=2)
    LTSETT = models.DecimalField(max_digits=15, decimal_places=2)
    CMSREG =  models.DecimalField(max_digits=15, decimal_places=2)
    LTSREG =  models.DecimalField(max_digits=15, decimal_places=2)
    HORAMOV = models.TimeField(auto_now_add=True)

class InventarioCombustibles(BaseModel):
    ESTACION = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    PRODUCTO = models.ForeignKey(Producto, on_delete=models.CASCADE)
    FECHA = models.DateField()
    FISICA =  models.DecimalField(max_digits=15, decimal_places=2)
    EXISTENCIA_CONTABLE =  models.DecimalField(max_digits=15, decimal_places=2)
    LTSVENTA =  models.DecimalField(max_digits=15, decimal_places=2)
    LTSMOV =  models.DecimalField(max_digits=15, decimal_places=2)
    VOLUMEN =   models.DecimalField(max_digits=15, decimal_places=2)
    DIFERENCIA =  models.DecimalField(max_digits=15, decimal_places=2)
    DIFERENCIA_ACUMULADA =  models.DecimalField(max_digits=15, decimal_places=2)

