from .db_config import Session, stations
from sqlalchemy import text
from contextlib import contextmanager
import pandas as pd
from core.stationdata.models import CATTABCUB, Estacion, Tanque, Producto
from django.utils.timezone import now

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()


def generate_cattabcub_query(stations):
    base_query = """
    SELECT '{station}' AS ESTACION, {station}_cattabcub.*
    FROM {station}_cattabcub
    """
    query_parts = [base_query.format(station=station) for station in stations]
    combined_query = "\nUNION ALL\n".join(query_parts)
    return text(combined_query)

def execute_query(query):
    with session_scope() as session:
        result_proxy = session.execute(query)
        columns = result_proxy.keys()
        data = [dict(zip(columns, row)) for row in result_proxy.fetchall()]
    return data


def fetch_data_tabcub():
    #query = generate_cattabcub_query(stations)
    #data = execute_query(query)

    df =  pd.read_csv('CATTABCUB.csv')
    df['ESTACION'] = df['ESTACION'].astype(str).str.zfill(3)
    df['TANQUE_ID'] = df['TANQUE_ID'].astype(str).str.zfill(2)
    Tanque.objects.all().delete()
    
    # Iterate over DataFrame and create CATTABCUB instances
    for _, row in df.iterrows():
        # Assuming Estacion model has a field that matches the 'ESTACION' value in df
        estacion_obj = Estacion.objects.get(Estacion_id=row['ESTACION'])  
        
        CATTABCUB.objects.create(
            ESTACION=estacion_obj,
            TANQUE_ID=row['TANQUE_ID'],
            CMS=row['CMS'],
            LITROS=row['LITROS'],
            STATUS=row.get('STATUS', 'A')  # Default to 'A' if STATUS is not in row
        )
    tank = pd.read_csv('TANQUES.csv')
    tank['ESTACION'] = tank['ESTACION'].astype(str).str.zfill(3)
    tank['TANQUE_ID'] = tank['TANQUE_ID'].astype(str).str.zfill(2)
    tank['PRODUCTO'] = tank['PRODUCTO'].astype(str).str.zfill(4)

    for _, row in tank.iterrows():
        # Assuming Estacion model has a field that matches the 'ESTACION' value in df
        estacion_obj = Estacion.objects.get(Estacion_id=row['ESTACION'])  
        prodcuto_obj    = Producto.objects.get(Producto_id=row['PRODUCTO'])
        Tanque.objects.create(
            tanque_id=f"{row['ESTACION']}-{row['TANQUE_ID']}-{row['PRODUCTO']}",
            Estacion=estacion_obj,
            Numero=row['TANQUE_ID'],
            Producto=prodcuto_obj,
            Vertical=row['VERTICAL'],
            Capacidad=row['CAPACIDAD'],
            Altura=row['ALTURA'],
            Diametro=row['DIAMETRO'],
            Existencia=0,
            Diferencia_Acumulada=0,
            Fecha_ultmodif = now(),
            Usuario_ultmodif="001"  # Default to 'A' if STATUS is not in row
        )
    return df.to_csv('CATTABCUB.csv', index=False)

# The following Python script is a hypothetical example of how to fetch data from a Django ORM, 
# fit a linear regression model to the data, and return the model parameters.
# Please note that to run this script, you would need to have a Django environment set up with the
# corresponding models (Estacion, Tanque, and CATTABCUB) and fields (Estacion_id, STATUS, CMS, LITROS, etc.).

from django.core.exceptions import ObjectDoesNotExist
from sklearn.linear_model import LinearRegression
import numpy as np

# Hypothetical Django models
# from myapp.models import Estacion, Tanque, CATTABCUB

def fetch_linear():
     # Fetch all CATTABCUB records with the desired columns
    cattabcub_records = CATTABCUB.objects.values('TANQUE_ID', 'CMS', 'LITROS', 'STATUS', 'ESTACION_id')
     # Turn the QuerySet into a Pandas DataFrame
    df = pd.DataFrame.from_records(cattabcub_records)

    # Convert 'cms' and 'litros' columns to float
    df['CMS'] = df['CMS'].astype(float)
    df['LITROS'] = df['LITROS'].astype(float)

    # Group by 'estacion_id' and 'tanque_id'
    grouped_df = df.groupby(['ESTACION_id', 'TANQUE_ID'])
    def find_highest_litros(grouped_data):
        highest_litros_values = {}

        for (estacion_id, tanque_id), group_data in grouped_data:
            # Find the index of the maximum 'LITROS' value in the group
            max_litros_idx = group_data['LITROS'].idxmax()

            # Retrieve the row corresponding to the maximum 'LITROS' value
            max_litros_row = group_data.loc[max_litros_idx]

            # Extract the 'CMS' and 'LITROS' values
            cms = max_litros_row['CMS']
            litros = max_litros_row['LITROS']

            # Store the results with the corresponding 'estacion_id' and 'tanque_id'
            highest_litros_values[(estacion_id, tanque_id)] = {'CMS': cms, 'LITROS': litros}

        return highest_litros_values

    # Get the highest LITROS values and corresponding CMS for each group
    highest_litros_for_groups = find_highest_litros(grouped_df)

    # Print the results
    for group, values in highest_litros_for_groups.items():
        estacion_id, tanque_id = group
        print(f"Estacion ID: {estacion_id}, Tanque ID: {tanque_id}, CMS: {values['CMS']}, LITROS: {values['LITROS']}")    
        
    return pd.DataFrame(highest_litros_for_groups).to_csv('GRUPOS.csv', index=False)

# Example usage:
# station_id = 1
# models_parameters = fetch_linear(station_id)
# print(models_parameters)

# Since we cannot execute Django ORM code outside of a Django environment, the above is a template.
# To actually run this, you would need to be within a Django project with the ORM properly configured.
