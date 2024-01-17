from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from .queries import *
from .db_config import stations, super_stations, Session, Session_sanblas

def execute_all_queries_and_process_data():
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

    @contextmanager
    def session_scope_sanblas():
        """Provide a transactional scope around a series of operations."""
        session = Session_sanblas()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_query(query):
        with session_scope() as session:
            result_proxy = session.execute(query)
            columns = result_proxy.keys()
            data = [dict(zip(columns, row)) for row in result_proxy.fetchall()]
        return data

    def execute_query_sanblas(query):
        with session_scope_sanblas() as session:
            result_proxy = session.execute(query)
            columns = result_proxy.keys()
            data = [dict(zip(columns, row)) for row in result_proxy.fetchall()]
        return data
    def process_data(df, drop_tanque=True):
        df['PRODUCTO'] = df['PRODUCTO'].astype(str)  # Convert PRODUCTO column to string
        df.loc[df.PRODUCTO == '1', 'PRODUCTO'] = '0002'
        df.loc[df.PRODUCTO == '3', 'PRODUCTO'] = '0001'
        df['TANQUE'] = df['TANQUE'].astype(str).str.zfill(2)
        if drop_tanque:
            df = df.groupby(['ESTACION', 'PRODUCTO', 'FECHA']).sum().reset_index().drop(columns=['TANQUE'])
        df['FECHA'] = pd.to_datetime(df['FECHA'])
        return df

    def process_data_med(df, drop_tanque=True):
        df['TANQUE'] = df['TANQUE'].astype(str).str.zfill(2)
        df['FECHA'] = pd.to_datetime(df['FECHA'])
        return df
    print(stations)
    # Define your queries here
    movvtacombust_query = generate_movvtacombust_query(stations)
    descargas_query =   generate_descargas_query(stations)
    pruebas_query =     generate_pruebas_query(stations)
    movmedtanq_query=   generate_medidas_query(stations)
    movdepprin_query=   generate_depprin_query(stations)
    movsuper_query = generate_super_query(super_stations)

    # Define your queries here
    movvtacombust_sanblas = generar_consulta_SANBLAS('cortesturno')
    descargas_sanblas =   generar_consulta_SANBLAS('compras')
    pruebas_sanblas =     generar_consulta_SANBLAS('ventasvolumetricos')
    #movmedtanq_sanblas=   generar_consulta_SANBLAS('inventario')
    movdepprin_sanblas=   generar_consulta_SANBLAS('depositoscorte')

    # List of queries to be executed
    queries_saga = [movvtacombust_query, descargas_query, pruebas_query, movmedtanq_query,
                    movdepprin_query,movsuper_query]
    queries_sanblas = [movvtacombust_sanblas, descargas_sanblas, pruebas_sanblas, #movmedtanq_sanblas,
                       movdepprin_sanblas]
    results_sanblas = {}
    results_saga = {}

    with ThreadPoolExecutor(max_workers=len(queries_saga)) as executor:
        future_to_query = {executor.submit(execute_query, query): query for query in queries_saga}
        for future in as_completed(future_to_query):
            query = future_to_query[future]
            try:
                results_saga[query] = future.result()
            except Exception as exc:
                print(f'Query generated an exception: {exc}')

    with ThreadPoolExecutor(max_workers=len(queries_sanblas)) as executor:
        future_to_query = {executor.submit(execute_query_sanblas, query): query for query in queries_sanblas}
        for future in as_completed(future_to_query):
            query = future_to_query[future]
            try:
                results_sanblas[query] = future.result()
            except Exception as exc:
                print(f'Query generated an exception: {exc}')
    return {
        "movsuper_data": pd.DataFrame(results_saga.get(movsuper_query, [])),
        "movvtacombust_data": pd.DataFrame(results_saga.get(movvtacombust_query, [])),
        "descargas_data": pd.DataFrame(results_saga.get(descargas_query, [])),
        "pruebas_data": pd.DataFrame(results_saga.get(pruebas_query, [])),
        "movdepprin_data": pd.DataFrame(results_saga.get(movdepprin_query, [])),
        "movmedtanq_data": pd.DataFrame(results_saga.get(movmedtanq_query, [])).assign(FECHA=lambda df: pd.to_datetime(df['FECHA'])),
        "vtasanblas_data": process_data(pd.DataFrame(results_sanblas.get(movvtacombust_sanblas, []))),
        "descsanblas_data": process_data(pd.DataFrame(results_sanblas.get(descargas_sanblas, []))),
        "pruebassanblas_data": process_data(pd.DataFrame(results_sanblas.get(pruebas_sanblas, []))).assign(FECHA=lambda df: pd.to_datetime(df['FECHA'])),
        #"movmedtanqsanblas_data": process_data_med(pd.DataFrame(results_sanblas.get(movmedtanq_sanblas, []))),
        "movdepprinsanblas_data": pd.DataFrame(results_sanblas.get(movdepprin_sanblas, [])).assign(FECHA=lambda df: pd.to_datetime(df['FECHA']))
    }




