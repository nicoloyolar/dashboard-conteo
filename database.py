import pyodbc
import logging

connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=192.168.31.168,1433;"
    "DATABASE=db_conteo_entero;"
    "UID=capturador;"
    "PWD=J7mo6uv97Y0x;"
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_connection():
    """Establece y devuelve una conexión a la base de datos."""
    try:
        return pyodbc.connect(connection_string)
    except Exception as e:
        logger.error(f"Error de conexión a la base de datos: {e}")
        raise

def execute_query(query, params=None, fetch=False):
    """Ejecuta una consulta SQL genérica. Devuelve los resultados si `fetch=True`."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or [])
            if fetch:
                return cursor.fetchall()
            conn.commit()
    except Exception as e:
        logger.error(f"Error al ejecutar la consulta: {e}")
        raise

def fetch_total_ultimo_dia():
    query = """
        SELECT COUNT(*) AS Cantidad, Etiqueta
        FROM [dbo].[ConteoProductos]
        WHERE CONVERT(DATE, Fecha) = CONVERT(DATE, GETDATE()) 
        GROUP BY Etiqueta
    """
    return execute_query(query, fetch=True)

def fetch_ult_15_min():
    query = """
        SELECT COUNT(*) AS Cantidad, Etiqueta
        FROM [dbo].[ConteoProductos]
        WHERE Fecha >= DATEADD(MINUTE, -15, GETDATE())
        GROUP BY Etiqueta
    """
    return execute_query(query, fetch=True)

def fetch_ult_45_min():
    query = """
        SELECT COUNT(*) AS Cantidad, Etiqueta
        FROM [dbo].[ConteoProductos]
        WHERE Fecha >= DATEADD(MINUTE, -45, GETDATE())
        GROUP BY Etiqueta
    """
    return execute_query(query, fetch=True)

def fetch_por_hora():
    query = """
        SELECT 
            COUNT(*) AS Cantidad, 
            Etiqueta, 
            DATEPART(HOUR, Fecha) AS Hora
        FROM 
            [dbo].[ConteoProductos]
        WHERE 
            CONVERT(DATE, Fecha) = CONVERT(DATE, GETDATE())  
            AND DATEPART(HOUR, Fecha) BETWEEN 00 AND 24
        GROUP BY 
            Etiqueta, DATEPART(HOUR, Fecha)
        ORDER BY 
            Hora
    """
    return execute_query(query, fetch=True)

def insert_conteo(etiqueta, fecha):
    query = """
        INSERT INTO [dbo].[ConteoProductos] (Etiqueta, Fecha)
        VALUES (?, ?)
    """
    execute_query(query, (etiqueta, fecha))

def insertar_conteo(etiqueta, cantidad, timestamp):
    """Inserta múltiples registros de conteo de productos."""
    for _ in range(cantidad):
        insert_conteo(etiqueta, timestamp)

