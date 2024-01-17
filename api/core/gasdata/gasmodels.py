from sqlalchemy import CHAR, Column, Date, Enum, Float, String, Time, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

def create_dynamic_model(station_id, base_class):
    class_name = f"{station_id}_{base_class.__name__}"
    return type(class_name, (base_class,), {'__tablename__': class_name, 'extend_existing':True})

class movdescargasdet(Base):
    __abstract__ = True
    IDFOL = Column(CHAR(10), primary_key=True, server_default=text("''"), comment='ID PRINCIPAL')
    FECHA = Column(Date, comment='FECHA DEL MOVIMIENTO')
    TANQUE = Column(String(30), comment='CODIGO DEL TANQUE ALMACENAMIENTO')
    CMSINI = Column( Float(5, True), comment='CENTIMETROS INICIAL')
    CMSFIN = Column(Float(5, True), comment='CENTIMETROS FINAL')
    LTSINI = Column(Float(12, True), comment='LITROS INICIAL')
    LTSFIN = Column(Float(12, True), comment='LITROS FINAL')
    LTSMOV = Column(Float(12, True), nullable=False, server_default=text("'0.00'"), comment='LITROS DEL MOVIMIENTO')
    STATUS = Column(String(1), comment='A= ACTIVO C= CANCELADO')

class movdepprin(Base):
    __table_args__ = {'comment': 'TABLA DE ALMACENAMIENTO DE DEPOSITOS BANCARIOS'}
    __abstract__ = True
    ID = Column(CHAR(7), primary_key=True, server_default=text("''"), comment='ID PRINCIPAL')
    FECHA = Column(Date, index=True, comment='FECHA DE ENVIO')
    HORA = Column(Time, nullable=False, server_default=text("'00:00:00'"), comment='HORA DEL ENVIO')
    FOLIO = Column(CHAR(25), nullable=False, server_default=text("''"), comment='FOLIO DE SELLOS DE SEGURIDAD')
    TIPO = Column(String(25), comment='TIPO DE DEPOSITO')
    CUENTA = Column(String(15), nullable=False, server_default=text("''"), comment='NUMERO DE CUENTA')
    SOBRES = Column(INTEGER(11), nullable=False, server_default=text("'0'"), comment='NUMERO DE SOBRES ENVIADOS')
    IMPORTE = Column(Float(12, True), comment='IMPORTE DEL DEPOSITO')
    CONCEPTO = Column(String(40), comment='COMENTARIO')
    USERMOV = Column(CHAR(22), nullable=False, server_default=text("''"), comment='USUARIO REALIZO EL ENVIO')
    STATUS = Column(Enum('A', 'P', 'C'), nullable=False, comment='STATUS DEL DEPOSITO ACTIVO-PAGADO-CANCELADO')


class movdescarga(Base):
    __abstract__ = True
    IDFOL = Column(String(8), primary_key=True, server_default=text("''"), comment='FOLIO DE DESCARGA')
    FECHA = Column(Date, nullable=False, index=True, server_default=text("'0000-00-00'"), comment='FECHA DE DESCARGA')
    HORA = Column(Time, nullable=False, server_default=text("'00:00:00'"), comment='HORA RECEPCION DESCARGA')
    TDA = Column(String(5), nullable=False, server_default=text("''"), comment='IDENTIFICADOR DE ZONA')
    FACTURA = Column(String(10), nullable=False, server_default=text("''"), comment='NUMERO DE FACTURA')
    COMBUSTIBLE = Column(String(35), nullable=False, server_default=text("''"), comment='NOMBRE COMBUSTIBLE')
    Costo = Column(Float(7, True), nullable=False, server_default=text("'0.00000'"), comment='COSTO DEL COMBUSTIBLE')
    LITROS = Column(Float(9, True), nullable=False, server_default=text("'0.00'"), comment='LITROS DESCARGADOS')
    IMPTOTAL = Column(Float(12, True), nullable=False, server_default=text("'0.00'"), comment='IMPORTE TOTAL DE LA FACTURA')
    VEHICULO = Column(String(20), nullable=False, server_default=text("''"), comment='VEHICULO PIPA PEMEX')
    CHOFER = Column(String(50), nullable=False, server_default=text("''"), comment='NOMBRE DEL CHOFER')
    RECIBIO = Column(String(50), nullable=False, server_default=text("''"), comment='NOMBRE RECIBIO DESCARGA')
    OBSERVACION = Column(String(150), nullable=False, server_default=text("''"), comment='ANOTACIONES')
    STATUS = Column(String(1), nullable=False, server_default=text("''"), comment='C=CANCELADO A=ACTIVO')
    USUARIO_MOV = Column(String(22), nullable=False, server_default=text("''"), comment='USUARIO REGISTRO MOVIMIENTO')
    FECH_MOV = Column(Date, nullable=False, server_default=text("'0000-00-00'"), comment='FECHA DEL MOVIMIENTO')
    HORA_MOV = Column(Time, nullable=False, server_default=text("'00:00:00'"), comment='HORA DEL MOVIMIENTO')
    BITACORA = Column(String(10), nullable=False, server_default=text("''"), comment='FOLIO DE BITACORA')


class movmedtanq(Base):
    __table_args__ = {'comment': 'TABLA DE MEDIDAS TANQUES'}
    __abstract__ = True

    ID = Column(String(10), primary_key=True, comment='FOLIO DEL REGISTRO')
    FECHA = Column(Date, comment='FECHA DEL MOVIMIENTO')
    TANQUE = Column(String(4), comment='CODIGO DEL TANQUE ALMACENAMIENTO')
    LTSETT = Column(Float(12, True), comment='LITROS ETT') #EQUIPO DE TELEMEDICIÓN DE TANQUES
    CMSREG = Column(Float(5, True), comment='CENTIMETROS REGLA')
    LTSREG = Column(Float(12, True), comment='LITROS REGLA')
    STATUS = Column(String(1), comment='A= ACTIVO C= CANCELADO')
    USERMOV = Column(String(45), comment='USUARIO ACTIVO')
    FECHMOV = Column(Date, comment='FECHA DEL MOVIMIENTO')
    HORAMOV = Column(Time, nullable=False, server_default=text("'00:00:00'"), comment='HORA DE CAPTURA')
    BITACORA = Column(String(10))


class movpagaut(Base):
    __table_args__ = {'comment': 'TABLA DE ALMACENAMIENTO DE PAGOS AUTORIZADOS'}
    __abstract__ = True
    ID = Column(CHAR(10), primary_key=True, server_default=text("''"), comment='FOLIO DEL REGISTRO')
    FECHA = Column(Date, index=True, comment='FECHA DEL DEPOSITO')
    TURNO = Column(Enum('0', '1', '2', '3', '4'), nullable=False, comment='NUMERO DE TURNO DE TRABAJO')
    TIPO = Column(String(35), nullable=False, comment='TIPO DE PAGO AUTORIZADO')
    DESCRIPCION = Column(String(80), nullable=False, server_default=text("''"), comment='DESCRIPCION DEL PAGO')
    RECIBO = Column(CHAR(10), nullable=False, server_default=text("''"), comment='NUMERO DE RECIBO')
    IMPORTE = Column(Float(12, True), comment='IMPORTE DEL DEPOSITO')
    ImpAplicado = Column(Float(12, True), nullable=False, server_default=text("'0.00'"), comment='IMPORTE APLICADO')
    STATUS = Column(Enum('A', 'P', 'C'), nullable=False, comment='STATUS DEL REGISTRO ACTIVO-CANCELADO-PAGADO')
    USERMOV = Column(CHAR(22), nullable=False, server_default=text("''"), comment='USUARIO QUE REALIZO EL MOVIMIENTO')
    FECH_MOV = Column(Date)
    HORA_MOV = Column(Time, nullable=False, server_default=text("'00:00:00'"), comment='HORA DEL MOVIMIENTO')
    BITACORA = Column(CHAR(10), nullable=False, server_default=text("''"), comment='NUMERO REGISTRO DE BITACORA')


class movsuper(Base):
    __table_args__ = {'comment': 'TABLA DE VENTA DE SUPERS'}
    __abstract__ = True
    ID = Column(String(10), primary_key=True, comment='FOLIO DEL REGISTRO')
    FECHA = Column(Date, comment='FECHA DEL PAGO DIVERSO')
    TURNO = Column(String(1), comment='NUMERO DE TURNO')
    FOLCORTE = Column(String(10), comment='FOLIO DEL CORTE')
    IMPEXCENT = Column(Float(12, True), nullable=False, server_default=text("'0.00'"), comment='IMPORTE DE VENTA EXCENTA DE IVA')
    IMPGRABAD = Column(Float(12, True), nullable=False, server_default=text("'0.00'"), comment='IMPORTE DE VENTA GRABADA')
    IMPIVA = Column(Float(12, True), nullable=False, server_default=text("'0.00'"), comment='IMPORTE DE IVA DE LA VENTA GRABADA')
    IMPVENTA = Column(Float(12, True), comment='IMPORTE DE VENTA')
    IMPENTREGA = Column(Float(12, True), nullable=False, server_default=text("'0.00'"), comment='IMPORTE ENTREGADO PARA DEPOSITAR')
    IMPDIFER = Column(Float(12, True), comment='IMPORTE DE DIFERENCIA')
    IMPCTRL = Column(Float(12, True), nullable=False, server_default=text("'0.00'"), comment='IMPORTE DE MERMA POR APLICACION')
    STATUS = Column(String(1), comment='C= CANCELADO V=VIGENTE')
    USERMOV = Column(String(22), comment='USUARIO QUE REALIZO EL MOVIMIENTO')
    FECH_MOV = Column(Date)
    HORA_MOV = Column(Time, nullable=False, server_default=text("'00:00:00'"), comment='HORA DEL MOVIMIENTO')
    BITACORA = Column(String(10))


class movvtacombust(Base):
    __table_args__ = {'comment': 'TABLA VENTAS DE COMBUSTIBLES'}
    __abstract__ = True
    ID = Column(CHAR(10), primary_key=True, server_default=text("''"), comment='FOLIO DE REGISTRO')
    FECHA = Column(Date, index=True, comment='FECHA DEL TURNO')
    TURNO = Column(Enum('1', '2', '3', '4'), nullable=False, comment='NUMERO DE TURNO')
    IDBOMBA = Column(CHAR(4), nullable=False, server_default=text("''"), comment='CODIGO DE LA BOMBA')
    POSCAR = Column(CHAR(4), nullable=False, server_default=text("''"), comment='POSICION DE CARGA')
    PRODUCTO = Column(CHAR(35), nullable=False, server_default=text("''"), comment='PRODUCTO QUE SURTE LA BOMBA')
    MANGUERA = Column(CHAR(15), nullable=False, comment='MANGUERA SURTIDORA')
    DISPENSARIO = Column(CHAR(40), nullable=False, server_default=text("''"), comment='DISPENSARIO PERTENECE LA BOMBA')
    TANQUE = Column(CHAR(2), nullable=False, server_default=text("''"), comment='CODIGO DEL TANQUE DE ALMACENAMIENTO')
    EMPLEADO = Column(CHAR(75), nullable=False, server_default=text("''"), comment='NOMBRE DEL EMPLEADO')
    LECTURAINI = Column(Float(12, True), comment='LECTURA INICIAL')
    LECTURAFIN = Column(Float(12, True), comment='LECTURA FINAL')
    LTSVENTA = Column(Float(12, True), comment='LISTROS DE VENTA')
    LtsCtrlInv = Column(Float(12, True), nullable=False, server_default=text("'0.000'"), comment='LITROS CONTROL DE INVENTARIO')
    LtsNewVent = Column(Float(12, True), nullable=False, server_default=text("'0.000'"), comment='LITROS VENTA MENOS CONTROL DE INVENTARIO')
    PRECIO = Column(Float(12, True), comment='PRECIO DE VENTA')
    IMPSUBT = Column(Float(12, True), nullable=False, server_default=text("'0.00'"), comment='IMPORTE SUBTOTAL')
    IMPIVA = Column(Float(12, True), nullable=False, server_default=text("'0.00'"), comment='IMPORTE IMPUESTO DE IVA')
    IMPIEPS = Column(Float(12, True), nullable=False, server_default=text("'0.000000'"), comment='IMPORTE IMPUESTO DE IEPS')
    IMPORTEVTA = Column(Float(12, True), comment='IMPORTE DE VENTA')
    TASAIVA = Column(Float(4, True), nullable=False, server_default=text("'0.00'"), comment='TASA DE IVA')
    TASAIEPS = Column(Float(6, True), nullable=False, server_default=text("'0.000000'"), comment='TASA DE IEPS')
    STATUS = Column(Enum('A', 'F'), nullable=False, comment='STATUS DEL REGISTRO ACTIVO-FINALIZADO')
    USERMOV = Column(CHAR(22), nullable=False, server_default=text("''"), comment='USUARIO QUE REALIZO EL MOVIMIENTO')
    FECH_MOV = Column(Date, comment='FECHA DEL MOVIMIENTO')
    HORA_MOV = Column(Time, comment='HORA DEL MOVIMIENTO')
    BITACORA = Column(CHAR(10), nullable=False, server_default=text("''"), comment='NUMERO REGISTRO DE BITACORA')


###############################################################################################################################
###############################################################################################################################