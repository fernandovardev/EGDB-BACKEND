# myapp/management/commands/update_data.py

from core.gasdata.DB.database_query import execute_all_queries_and_process_data
from core.gasdata.DB.data_processing import process_and_merge_data
from django.core.management.base import BaseCommand
from django.db import transaction
from core.stationdata.models import Compras, Ventas, PruebaBombas, ReporteDinero, Estacion, Producto, MOVMEDTANQ
import logging
 
stations = list(Estacion.objects.filter(is_WHOLESALE=False).values_list('Estacion_id', flat=True))

class Command(BaseCommand):
    help = 'Fetches, clears, and updates the database with new data'

    def handle(self, *args, **kwargs):
        try:
            efectivo_df, compras_df, summed_pruebas, ventas_df, movmedtanq_df = process_and_merge_data(execute_all_queries_and_process_data())
            logging.info(f"Data processed: {efectivo_df.shape}, {compras_df.shape}, {summed_pruebas.shape}, {ventas_df.shape}")
            with transaction.atomic():
                # Clear existing data

#filter(Estacion_id__in=stations)
                estaciones = {e.Estacion_id: e for e in Estacion.objects.all()}
                productos = {p.Producto_id: p for p in Producto.objects.all()}
                # Create Compras objects
                Compras.objects.filter(Estacion__is_WHOLESALE=False).delete()
                for _, row in compras_df.iterrows():
                    Compras.objects.create(
                        Estacion=estaciones[row['ESTACION']],
                        Producto=productos[row['PRODUCTO']],
                        volumen=row['LTSMOV'],
                        Fecha=row['FECHA']
                    )

                # Create Ventas objects
                Ventas.objects.filter(Estacion__is_WHOLESALE=False).delete()
                for _, row in ventas_df.iterrows():
                    Ventas.objects.create(
                        Estacion=estaciones[row['ESTACION']],
                        Producto=productos[row['PRODUCTO']],
                        volumen=row['LTSVENTA'],
                        Fecha=row['FECHA']
                    )

                # Create PruebaBombas objects
                PruebaBombas.objects.filter(Estacion__is_WHOLESALE=False).delete()
                for _, row in summed_pruebas.iterrows():
                    PruebaBombas.objects.create(
                        Estacion=estaciones[row['ESTACION']],
                        Producto=productos[row['PRODUCTO']],
                        volumen=row['VOLUMEN'],
                        Fecha=row['FECHA']
                    )

                # Create ReporteDinero objects
                ReporteDinero.objects.filter(Estacion__is_WHOLESALE=False).delete()
                for _, row in efectivo_df.iterrows():
                    ReporteDinero.objects.create(
                        Estacion=estaciones[row['ESTACION']],
                        Fecha=row['FECHA'],
                        PANAMERICANO=row['PANAMERICANO'],
                        SUPER=row['SUPER']
                    )

                MOVMEDTANQ.objects.filter(ESTACION__is_WHOLESALE=False).exclude(ESTACION__Estacion_id='004').delete()
                for _, row in movmedtanq_df.iterrows():
                    try:
                        MOVMEDTANQ.objects.create(
                            FECHA =row['FECHA'],
                            ESTACION = estaciones.get(row['ESTACION_id'], None),
                            TANQUE_ID = row['TANQUE'],
                            LTSETT = row['LTSETT'],
                            CMSREG = row['CMSREG'],
                            LTSREG = row['LTSREG'],
                            HORAMOV = row['HORAMOV'], # Changed from 'LTSREG' to 'HORAMOV'
                        )
                    except KeyError as e:
                        print(f"KeyError for date: {e}")
                       
        except Exception as e:
            logging.error(f"Error updating the database: {e}")
            raise e