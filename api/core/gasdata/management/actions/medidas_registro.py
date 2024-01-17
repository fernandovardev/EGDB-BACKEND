from core.stationdata.models import Tanque, Estacion, CATTABCUB, MOVMEDTANQ, Estacion
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal

def fetch_tanks_tabcub(station):
    try:
        estacion_obj = Estacion.objects.get(Estacion_id=station)
    except ObjectDoesNotExist:
        return {'error': f'Estacion with id {station} does not exist.'}

    tanques = Tanque.objects.filter(Estacion_id=estacion_obj, STATUS='A')

    tanks_data = {}
    for tanque in tanques:
        tanks_data[tanque.tanque_id] = {
            'Numero': tanque.Numero,
            'Status': tanque.STATUS,
            'Estacion_id': tanque.Estacion_id,
            'Producto_id': tanque.Producto_id,
            'Vertical': tanque.Vertical,
            'Capacidad': tanque.Capacidad,
            'Altura': tanque.Altura,
            'Diametro': tanque.Diametro
        }

    #print(tanks_data)
    return tanks_data

from django.db.models import F
from django.db import transaction     
from datetime import datetime
from django.db.models import Q

def register_tank_measurements(data):
    try:
        with transaction.atomic():
            date = datetime.strptime(data['date'], '%Y-%m-%d').date()
            station = Estacion.objects.get(Estacion_id=data['station'])

            for tank_id, tank_data in data['tanks'].items():
                tank_number = tank_id.split('-')[1]  # Assuming '004-01-0002' format, extract '01'

                # Check if a record exists with the same date, station, and tank_number
                existing_record = MOVMEDTANQ.objects.filter(
                    FECHA=date, ESTACION=station, TANQUE_ID=tank_number
                ).first()

                if existing_record:
                    # Update the existing record
                    existing_record.LTSETT = tank_data['LTSETT']
                    existing_record.CMSREG = tank_data['CMSREG']
                    existing_record.LTSREG = tank_data['LTSREG']
                    existing_record.save()
                else:
                    # Create a new record
                    MOVMEDTANQ.objects.create(
                        FECHA=date,
                        ESTACION=station,
                        TANQUE_ID=tank_number,
                        LTSETT=tank_data['LTSETT'],
                        CMSREG=tank_data['CMSREG'],
                        LTSREG=tank_data['LTSREG']
                    )

                # Update Tanque object
                Tanque.objects.filter(Estacion=station, Numero=tank_number).update(
                    Existencia=tank_data['LTSREG'], # Use the calculated LTSREG value
                    FECHAMOV=date
                )
        return {'message': 'Tank measurements registered successfully.'}, None
    except Estacion.DoesNotExist:
        return None, {'error': 'Station not found.', 'status': 404}
    except Tanque.DoesNotExist:
        return None, {'error': 'Tank not found for the given station.', 'status': 404}
    except Exception as e:
        # More detailed error handling
        return None, {'error': f'An error occurred: {str(e)}', 'status': 400}