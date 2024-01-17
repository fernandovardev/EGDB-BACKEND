from django.core.management.base import BaseCommand
from django.db import transaction
from core.stationdata.models import MOVMEDTANQ, Tanque, Ventas, PruebaBombas, Compras, Estacion, Producto, InventarioCombustibles
from datetime import datetime
import logging
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

class Command(BaseCommand):
    help = 'Updates inventory based on existing measures'

    def handle(self, *args, **kwargs):
        logging.basicConfig(filename='inventory_update_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')
        logging.info("Starting inventory update")

        start_date = datetime(2022, 12, 1).date().strftime("%Y-%m-%d")
        end_date = datetime.now().date().strftime("%Y-%m-%d")

        try:
            self.update_inventory_bulk(start_date, end_date)
            logging.info("Completed inventory update")
        except Exception as e:
            logging.error(f"Inventory update failed: {e}")

    def update_inventory_bulk(self, start_date, end_date):
        InventarioCombustibles.objects.all().delete()
        estaciones = {e.Estacion_id: e for e in Estacion.objects.all()}
        productos = {p.Producto_id: p for p in Producto.objects.all()}

        tanques, movmedtanq_records, ventas_records, pruebas_records, compras_records = self.fetch_data(start_date, end_date)
        inventario = self.merge_and_process_data(tanques, movmedtanq_records, ventas_records, pruebas_records, compras_records)
        self.create_inventory_entries(inventario, estaciones, productos)

        return inventario

    def fetch_data(self, start_date, end_date):
        # Fetch and prepare Tanques data
        tanques = pd.DataFrame(
            Tanque.objects.all().values("Numero", "Estacion_id", "Producto_id")
        ).rename(columns={"Numero": "TANQUE_ID", "Estacion_id": "ESTACION_id", "Producto_id": "PRODUCTO"})

        # Fetch MOVMEDTANQ records
        movmedtanq_records = pd.DataFrame(
            MOVMEDTANQ.objects.filter(FECHA__range=(start_date, end_date)).values("FECHA", "TANQUE_ID", "ESTACION_id", "LTSREG")
        )

        # Fetch Ventas, Pruebas and Compras records
        ventas_records = self.fetch_transaction_data(Ventas, "VENTA", start_date, end_date)
        pruebas_records = self.fetch_transaction_data(PruebaBombas, "PRUEBAS", start_date, end_date)
        compras_records = self.fetch_transaction_data(Compras, "COMPRAS", start_date, end_date)

        return tanques, movmedtanq_records, ventas_records, pruebas_records, compras_records

    def fetch_transaction_data(self, model, column_name, start_date, end_date):
        return pd.DataFrame(
            model.objects.filter(Fecha__range=(start_date, end_date)).values("Estacion_id", "Producto_id", "volumen", "Fecha")
        ).rename(columns={"Estacion_id": "ESTACION_id", "Producto_id": "PRODUCTO", "volumen": column_name, "Fecha": "FECHA"})

    def merge_and_process_data(self, tanques, movmedtanq_records, ventas_records, pruebas_records, compras_records):
        # Merge and process data to calculate inventory details
        movmedtanq_records = movmedtanq_records.merge(tanques, on=['TANQUE_ID', 'ESTACION_id'], how="outer")
        movmedtanq_records = movmedtanq_records.groupby(['ESTACION_id', 'PRODUCTO', 'FECHA']).sum().reset_index().drop(columns=['TANQUE_ID'])
        inventario = movmedtanq_records.merge(ventas_records, on=['PRODUCTO', 'ESTACION_id', 'FECHA'], how="inner").fillna(0)

        inventario = inventario.merge(pruebas_records, on=['PRODUCTO', 'ESTACION_id', 'FECHA'], how="left").fillna(0)
        inventario = inventario.merge(compras_records, on=['PRODUCTO', 'ESTACION_id', 'FECHA'], how="left").fillna(0)
        inventario['FECHA'] = pd.to_datetime(inventario['FECHA'])

        inventario = inventario.groupby(['PRODUCTO', 'ESTACION_id']).apply(self.calculate_diferencia).reset_index(drop=True)
        inventario = inventario.groupby(['PRODUCTO', 'ESTACION_id', inventario['FECHA'].dt.to_period('M')]).apply(self.calculate_acumulada).reset_index(drop=True)
        return inventario

    def calculate_diferencia(self, group):
        three_decimals = Decimal('0.001')
        group['EXISTENCIA_CONTABLE'] = (group['LTSREG'].shift(periods=1, fill_value=0).apply(Decimal) -
                                        group['VENTA'].apply(Decimal) +
                                        group['COMPRAS'].apply(Decimal) +
                                        group['PRUEBAS'].apply(Decimal))\
                                        .apply(lambda x: x.quantize(three_decimals, rounding=ROUND_HALF_UP))
        group['DIFERENCIA'] = (group['LTSREG'].apply(Decimal) -
                               group['EXISTENCIA_CONTABLE']\
                              .apply(Decimal))\
                              .apply(lambda x: x.quantize(three_decimals, rounding=ROUND_HALF_UP))
        return group

    def calculate_acumulada(self, group):
        group['DIFERENCIA ACUMULADA'] = group['DIFERENCIA'].cumsum()
        group.loc[group['FECHA'].dt.is_month_start, 'DIFERENCIA ACUMULADA'] = group['DIFERENCIA']
        return group

    def create_inventory_entries(self, inventario, estaciones, productos):
        with transaction.atomic():
            for _, row in inventario.iterrows():
                InventarioCombustibles.objects.create(
                    ESTACION=estaciones[row['ESTACION_id']],
                    PRODUCTO=productos[row['PRODUCTO']],
                    FECHA=row['FECHA'],
                    FISICA=row['LTSREG'],
                    EXISTENCIA_CONTABLE=row['EXISTENCIA_CONTABLE'],
                    LTSVENTA=row['VENTA'],
                    LTSMOV=row['COMPRAS'],
                    VOLUMEN=row['PRUEBAS'],
                    DIFERENCIA=row['DIFERENCIA'],
                    DIFERENCIA_ACUMULADA=row['DIFERENCIA ACUMULADA']
                )

# End of the Command class
