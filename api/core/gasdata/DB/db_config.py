# Standard library imports
from contextlib import contextmanager
from collections import defaultdict
from datetime import date, datetime, timedelta
import csv
from itertools import product

# Third-party imports
import numpy as np
import pandas as pd
import xlsxwriter
from concurrent.futures import ThreadPoolExecutor, as_completed
from decimal import Decimal
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment, numbers
from openpyxl.utils import get_column_letter

# Django specific imports
from django.db import transaction
from django.db.models import F
from django.db.utils import IntegrityError

# Models
from core.stationdata.models import *
######################################################################################################################################################################################################################################################################################################################################
######################################################################################################################################################################################################################################################################################################################################
######################################################################################################################################################################################################################################################################################################################################
# Constants
DATABASE_SAGA = "mysql+mysqlconnector://Desarrollo1:aGuila01@corpaguila.no-ip.net:3306/saga"
DATABASE_ARREIN = "mssql+pymssql://Arrein_Factura:Fact1433@52.52.211.110/Flotillas_Arrein"

# Stations list and product order data
estaciones = Estacion.objects.filter(is_WHOLESALE=False).exclude(Estacion_id__in=['001','004', '008']).values_list('Estacion_id', flat=True)
stations = list(estaciones)
estaciones = Estacion.objects.filter(is_SUPER=True).values_list('Estacion_id', flat=True)
super_stations = list(estaciones)
special_stations = ["016", "018", "019"]

data_query = Tanque.objects.all().values_list('Estacion__Estacion_id', 'Producto__Producto_id', 'Numero')
data = {
    'ESTACION': [int(estacion) for estacion, _, _ in data_query],
    'PRODUCTO': [producto for _, producto, _ in data_query],
    'TANQUE': [int(numero) for _, _, numero in data_query]
}

product_order_query = Tanque.objects.all().values_list('Estacion__Estacion_id', 'Producto__Producto_id').distinct()
product_order = {
    'ESTACION': [int(estacion) for estacion, _ in product_order_query],
    'PRODUCTO': [producto for _, producto in product_order_query]
}



######################################################################################################################################################################################################################################################################################################################################
######################################################################################################################################################################################################################################################################################################################################
######################################################################################################################################################################################################################################################################################################################################

# Database connection setup
def create_db_engine(database_url):
    return create_engine(
        database_url, 
        max_overflow=11, 
        pool_recycle=1800, 
        pool_pre_ping=True, 
        echo=False
    )

ENGINE_SAGA = create_db_engine(DATABASE_SAGA)
ENGINE_ARREIN = create_db_engine(DATABASE_ARREIN)

Session = sessionmaker(bind=ENGINE_SAGA)
Session_sanblas = sessionmaker(bind=ENGINE_ARREIN)

######################################################################################################################################################################################################################################################################################################################################
######################################################################################################################################################################################################################################################################################################################################
######################################################################################################################################################################################################################################################################################################################################
def create_stock_df(data):
    df = pd.DataFrame(data)
    df['TANQUE'] = df['TANQUE'].astype(str).str.zfill(2)
    df['PRODUCTO'] = df['PRODUCTO'].astype(str).str.zfill(4)
    df['ESTACION'] = df['ESTACION'].astype(str).str.zfill(3)
    return df.sort_values(['ESTACION', 'PRODUCTO'])

def create_dispen_df():
    dispen_data = list(Dispensario.objects.all().values("codigo", "NumeroTanque", "Producto_id", "Estacion_id"))
    df = pd.DataFrame(dispen_data)
    df = df.rename(columns={'NumeroTanque': 'numerotanque', 'Producto_id': 'producto_id', 'Estacion_id': 'Station_id'})
    df['numerotanque'] = df['numerotanque'].astype(str).str.zfill(2)
    df['producto_id'] = df['producto_id'].astype(str).str.zfill(4)
    df['Station_id'] = df['Station_id'].astype(str).str.zfill(3)
    return df

def create_estaciones_df():
    estaciones_data = list(Estacion.objects.all().values("Estacion_id", "Estacion_Nombre", "Empresa_id"))
    df = pd.DataFrame(estaciones_data)
    df = df.rename(columns={'Estacion_id': 'ESTACION_ID', 'Estacion_Nombre': 'ESTACION_NOMBRE', 'Empresa_id': 'COMPANY_ID'})
    df['ESTACION_ID'] = df['ESTACION_ID'].astype(str).str.zfill(3)
    df['COMPANY_ID'] = df['COMPANY_ID'].astype(str).str.zfill(3)

    return df

def create_productos_df():
    productos_data = list(Producto.objects.all().values("Producto_id", "Nombre"))
    df = pd.DataFrame(productos_data)
    df = df.rename(columns={'Producto_id': 'PRODUCTO_ID', 'Nombre': 'PRODUCTO_NOMBRE'})
    df['PRODUCTO_ID'] = df['PRODUCTO_ID'].astype(str).str.zfill(4)
    return df

def create_empresa_df():
    empresa_data = list(Empresa.objects.all().values("Empresa_id", "Razon_social"))
    df = pd.DataFrame(empresa_data)
    df = df.rename(columns={'Empresa_id': 'EMPRESA_ID', 'Razon_social': 'EMPRESA_RAZONSOCIAL'})
    df['EMPRESA_ID'] = df['EMPRESA_ID'].astype(str).str.zfill(3)
    return df


def get_inventory_data_df():
    data = list(InventarioCombustibles.objects.all().values())
    df = pd.DataFrame(data)\
    .rename(columns={
        "ESTACION_id":"ESTACION",
        "PRODUCTO_id":"PRODUCTO",
        
    })\
    .drop(columns=['STATUS','FECHAMOV'])

    df['FECHA'] = pd.to_datetime(df['FECHA'])
    return df

def get_financial_data_df():
    data = list(ReporteDinero.objects.all().values())
    df = pd.DataFrame(data)\
    .rename(columns={
        "Estacion_id":"ESTACION",
        "Fecha":"FECHA"

        
    })\
    .drop(columns=['STATUS','FECHAMOV','Reporte_dinero_id'])
    print(df)
    df['FECHA'] = pd.to_datetime(df['FECHA'])
    return df

######################################################################################################################################################################################################################################################################################################################################










