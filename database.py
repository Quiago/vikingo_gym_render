import psycopg2
import os

# Conexión a la base de datos PostgreSQL
def connect_db():
    url = 'postgresql+psycopg2://dwh_ingestion:bBHy5fDtaE!3rNM2123443412fd*@51.79.102.5:5433/dhw_demo_de'
    return psycopg2.connect(url)
    #return psycopg2.connect(os.getenv("DATABASE_URL"))

# Guardar datos del cliente
def save_client_to_db(client_data):
    """
    Guarda los datos del cliente en la base de datos.
    """
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO clients (name, lastname, gender, id_card, phone, membership)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (
        client_data["name"],
        client_data["lastname"],
        client_data["gender"],
        client_data["id_card"],
        client_data["phone"],
        client_data["membership"],
    )
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()
