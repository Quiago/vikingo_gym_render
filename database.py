import psycopg2
from psycopg2 import sql

DATABASE_URL = "postgresql://postgres:kALssRbWZylChNDDJuSxcONXxLwXtVLM@postgres.railway.internal:5432/railway"

# Initialize PostgreSQL database and create the tables if they don't exist
def initialize_db():
    """
    Creates the database tables if they don't exist.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL,sslmode='require')
    except Exception as e:
        print(e)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        chat_id TEXT PRIMARY KEY,
        role TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        chat_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        lastname TEXT NOT NULL,
        gender TEXT NOT NULL,
        id_card TEXT NOT NULL,
        phone TEXT NOT NULL,
        membership TEXT NOT NULL,
        init_date DATE NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workers (
        chat_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        lastname TEXT NOT NULL,
        id_card TEXT NOT NULL,
        phone TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trainers (
        chat_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        lastname TEXT NOT NULL,
        id_card TEXT NOT NULL,
        phone TEXT NOT NULL
    )
    """)

    conn.commit()
    cursor.close()
    conn.close()

# Connect to the PostgreSQL database
def connect_db():
    """
    Connects to the PostgreSQL database.
    """
    return psycopg2.connect(DATABASE_URL)  # Returns a connection object

def save_user(data):
    """
    Save the user's data to the database.
    """
    conn = connect_db()
    cursor = conn.cursor()  

    query = """
    INSERT INTO users (chat_id, role)
    VALUES (?, ?)
    """ 
    values = (data['chat_id'], data['role'])
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

# Save client data to the SQLite database
def save_client_to_db(data):
    """
    Save the client's data to the database.
    """
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO clients (chat_id, name, lastname, gender, id_card, phone, membership, init_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    values = ( 
        data["chat_id"],
        data["name"],
        data["lastname"],
        data["gender"],
        data["id_card"],
        data["phone"],
        data["membership"],
        data["init_date"]
    ) 
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

def save_worker_to_db(data):
    """
    Save the worker's data to the database.
    """
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO workers (chat_id, name, lastname, id_card, phone)
    VALUES (?, ?, ?, ?, ?)
    """
    values = ( 
        data["chat_id"],
        data["name"],
        data["lastname"],
        data["id_card"],
        data["phone"]
    ) 
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

def save_trainer_to_db(data):
    """
    Save the trainer's data to the database.
    """
    conn = connect_db()
    cursor = conn.cursor()

    query = """
    INSERT INTO trainers (chat_id, name, lastname, id_card, phone)
    VALUES (?, ?, ?, ?, ?)
    """
    values = ( 
        data["chat_id"],
        data["name"],
        data["lastname"],
        data["id_card"],
        data["phone"]
    ) 
    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()

def get_role(chat_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE chat_id = ?", (chat_id,))
    role = cursor.fetchone()
    cursor.close()
    conn.close()
    return role[0] if role else None

def get_payment_date(chat_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT init_date FROM clients WHERE chat_id = ?", (chat_id,))
    date = cursor.fetchone()
    cursor.close()
    conn.close()
    return date[0] if date else None
