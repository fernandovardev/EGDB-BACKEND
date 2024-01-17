from sqlalchemy import text

###################################################################################################################################################################
###################################################################################################################################################################
######################################################### CONSULTAS PARA BASES DE DATOS ###########################################################################
###################################################################################################################################################################
###################################################################################################################################################################

# Generate the query
def generate_movvtacombust_query(stations):
    base_query = """
    SELECT '{station}' AS ESTACION, FECHA, PRODUCTO, LTSVENTA, TURNO
    FROM {station}_movvtacombust
    WHERE FECHA BETWEEN '2022-12-01' AND '2024-01-31' 
    AND STATUS != 'C'
    """
    query_parts = [base_query.format(station=station) for station in stations]
    combined_query = "\nUNION ALL\n".join(query_parts)
    return text(combined_query)

def generate_descargas_query(stations):
    # Base query format with JOIN to include movdescargas
    base_query = """
    SELECT '{station}' AS ESTACION, FECHA, LITROS AS LTSMOV, COMBUSTIBLE AS PRODUCTO
    FROM {station}_movdescargas
    WHERE FECHA BETWEEN '2022-12-01' AND '2024-01-31' 
    AND STATUS != 'C'
    """
    
    # Generate each station's query and combine with UNION ALL
    query_parts = [base_query.format(station=station) for station in stations]
    combined_query = "\nUNION ALL\n".join(query_parts)
    
    # Convert the combined query string into a text clause
    return text(combined_query)
    
def generate_pruebas_query(stations):
    # Base query format
    base_query = """
    SELECT '{station}' AS ESTACION, FECHA, DESCRIPCION
    FROM {station}_movpagaut
    WHERE FECHA BETWEEN '2022-12-01' AND '2024-01-31' 
    AND STATUS != 'C'
    AND TIPO = '06- AUTOJARREO'
    """
    
    # Generate each station's query and combine with UNION ALL
    query_parts = [base_query.format(station=station) for station in stations]
    combined_query = "\nUNION ALL\n".join(query_parts)
    
    # Convert the combined query string into a text clause
    return text(combined_query)

def generate_medidas_query(stations):
    # Base query format
    base_query = """
    SELECT '{station}' AS ESTACION_id, TANQUE, LTSREG, FECHA, FECHMOV as FECHAMOV, HORAMOV, CMSREG, LTSETT
    FROM {station}_movmedtanq
    WHERE FECHA BETWEEN '2022-12-01' AND '2024-01-31' 
    AND STATUS != 'C'
    """
    
    # Generate each station's query and combine with UNION ALL
    query_parts = [base_query.format(station=station) for station in stations]
    combined_query = "\nUNION ALL\n".join(query_parts)
    
    # Convert the combined query string into a text clause
    return text(combined_query)

def generate_depprin_query(stations):
    # Base query format
    base_query = """
    SELECT '{station}' AS ESTACION, IMPORTE, FECHA
    FROM {station}_movdepprin
    WHERE FECHA BETWEEN '2022-12-01' AND '2024-01-31' 
    AND STATUS != 'C'
    """
    
    # Generate each station's query and combine with UNION ALL
    query_parts = [base_query.format(station=station) for station in stations]
    combined_query = "\nUNION ALL\n".join(query_parts)
    
    # Convert the combined query string into a text clause
    return text(combined_query)

def generate_super_query(stations):
    # Base query format
    base_query = """
    SELECT '{station}' AS ESTACION, IMPVENTA, FECHA
    FROM {station}_movsuper
    WHERE FECHA BETWEEN '2022-12-01' AND '2024-01-31' 
    AND STATUS != 'C'
    """
    
    # Generate each station's query and combine with UNION ALL
    query_parts = [base_query.format(station=station) for station in stations]
    combined_query = "\nUNION ALL\n".join(query_parts)
    
    # Convert the combined query string into a text clause
    return text(combined_query)


def generar_consulta_SANBLAS(query_type):
    # Base query templates for each type
    queries = {
        "cortesturno": """
            SELECT 
                '004' AS ESTACION,
                md.idTanque as TANQUE, 
                md.IdProducto as PRODUCTO, 
                SUM(dcb.Cantidad) as LTSVENTA,
                ct.FechaTrabajo as FECHA
            FROM 
                CortesTurno ct
            JOIN 
                DetallesCTCombustibles dcb ON ct.idCorteTurno = dcb.IdCorteTurno
            JOIN 
                MangueraDispensario md ON dcb.IdMangueraDispensario = md.IdMangueraDispensario
            WHERE 
                CAST(ct.FechaTrabajo AS DATE) BETWEEN '2022-12-01' AND '2024-01-31'
            GROUP BY 
                md.idTanque, md.IdProducto, ct.FechaTrabajo
        """,
        "compras": """
            SELECT 
                '004' AS ESTACION,
                cdt.idTanque as TANQUE, 
                cd.idProducto as PRODUCTO, 
                SUM(cd.Cantidad) as LTSMOV,
                c.Fecha as FECHA
            FROM 
                COMPRAS c
            JOIN 
                ComprasDetalleTanques cdt ON c.idCompra = cdt.IdCompra
            JOIN 
                ComprasDetalle cd ON c.idCompra = cd.IdCompra
            WHERE 
                CAST(c.Fecha AS DATE) BETWEEN '2022-12-01' AND '2024-01-31'
            GROUP BY 
                cdt.idTanque, cd.idProducto, c.Fecha
        """,
        "inventario": """
            SELECT 
                '004' AS ESTACION_id,
                ic.idTanque as TANQUE, 
                ic.ExistenciaReal as LTSETT,
                ic.FechaRegistro AS FECHA,
                ic.FechaRegistro AS FECHAMOV,
                GETDATE() AS HORAMOV
            FROM 
                InventarioCombustibles ic
            JOIN
                Tanques t ON ic.idTanque = t.IdTanque           
            
        """,
        "depositoscorte": """
            SELECT 
                '004' as ESTACION,
                FechaDeposito as FECHA,
                TotalDeposito as PANAMERICANO,
                0 as SUPER
            FROM 
                DepositosCorte
            WHERE 
                FechaDeposito  BETWEEN '2022-12-01' AND '2024-01-31'
        """,
        "ventasvolumetricos": """
            SELECT 
               '004' AS ESTACION,
                md.idTanque as TANQUE, 
                t.IdProducto as PRODUCTO, 
                vv.Volumen2 as VOLUMEN,
                vv.FechaHora AS FECHA
            FROM 
                VentasVolumetricos vv
            JOIN 
                Dispensarios d ON vv.NoDispensario = d.NoDispensario
            JOIN 
                MangueraDispensario md ON d.idDispensario = md.IdDispensario
            JOIN 
                Tanques t ON md.idTanque = t.IdTanque
            WHERE 
                CAST(vv.FechaHora AS DATE)  BETWEEN '2022-12-01' AND '2024-01-31' AND vv.tipoventa = 3
        """
    }
    # Choose the query template based on the query_type
    query_template = queries.get(query_type)
    if not query_template:
        raise ValueError(f"Query type {query_type} is not defined.")

    # Replace placeholders with actual values
    query = query_template.format()

    return text(query)


###################################################################################################################################################################
