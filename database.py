from sqlalchemy import create_engine, text
from datetime import datetime


# PostgreSQL connection URL
#DATABASE_URL = "postgresql+psycopg2://postgres:kALssRbWZylChNDDJuSxcONXxLwXtVLM@postgres.railway.internal:5432/railway"
DATABASE_URL = "postgresql+psycopg2://dwh_ingestion:bBHy5fDtaE!3rNM2123443412fd*@51.79.102.5:5433/dhw_demo_de"
# Initialize the database engine
engine = create_engine(DATABASE_URL)

# Initialize the database (create tables)
def initialize_db():
    """
    Creates all tables in the database.
    """
    with engine.begin() as connection:
        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            chat_id TEXT PRIMARY KEY,
            role TEXT NOT NULL
        );
        """))

        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS progress (
            chat_id TEXT NOT NULL,
            measure_date TEXT NOT NULL,
            age TEXT NOT NULL,
            weight TEXT NULL,
            height TEXT NULL,
            imc TEXT NULL,
            corporal_fat TEXT NULL
        );
        """))

        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS clients (
            chat_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            lastname TEXT NOT NULL,
            gender TEXT NOT NULL,
            id_card TEXT NOT NULL,
            phone TEXT NOT NULL,
            membership TEXT NOT NULL,
            init_date DATE NOT NULL
        );
        """))

        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS workers (
            chat_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            lastname TEXT NOT NULL,
            id_card TEXT NOT NULL,
            phone TEXT NOT NULL
        );
        """))

        connection.execute(text("""
        CREATE TABLE IF NOT EXISTS trainers (
            chat_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            lastname TEXT NOT NULL,
            id_card TEXT NOT NULL,
            phone TEXT NOT NULL
        );
        """))

# CRUD operations
def save_user(data):
    """
    Save a user's data to the database.
    """
    with engine.begin() as connection:
        query = text("""
        INSERT INTO users (chat_id, role)
        VALUES (:chat_id, :role)
        ON CONFLICT (chat_id) DO UPDATE
        SET role = EXCLUDED.role;
        """)
        connection.execute(query, {"chat_id": str(data["chat_id"]), "role": str(data["role"])})

def save_client_to_db(data):
    """
    Save a client's data to the database.
    """
    with engine.begin() as connection:
        query = text("""
        INSERT INTO clients (chat_id, name, lastname, gender, id_card, phone, membership, init_date)
        VALUES (:chat_id, :name, :lastname, :gender, :id_card, :phone, :membership, :init_date)
        ON CONFLICT (chat_id) DO UPDATE
        SET 
            name = EXCLUDED.name,
            lastname = EXCLUDED.lastname,
            gender = EXCLUDED.gender,
            id_card = EXCLUDED.id_card,
            phone = EXCLUDED.phone,
            membership = EXCLUDED.membership,
            init_date = EXCLUDED.init_date;
        """)
        connection.execute(query, {
            "chat_id": str(data["chat_id"]),
            "name": str(data["name"]),
            "lastname": str(data["lastname"]),
            "gender": str(data["gender"]),
            "id_card": str(data["id_card"]),
            "phone": str(data["phone"]),
            "membership": str(data["membership"]),
            "init_date": datetime.strptime(data["init_date"], '%d/%m/%Y').strftime('%Y-%m-%d')
        })

def save_worker_to_db(data):
    """
    Save a worker's data to the database.
    """
    with engine.begin() as connection:
        query = text("""
        INSERT INTO workers (chat_id, name, lastname, id_card, phone)
        VALUES (:chat_id, :name, :lastname, :id_card, :phone)
        ON CONFLICT (chat_id) DO UPDATE
        SET 
            name = EXCLUDED.name,
            lastname = EXCLUDED.lastname,
            id_card = EXCLUDED.id_card,
            phone = EXCLUDED.phone;
        """)
        connection.execute(query, {
            "chat_id": str(data["chat_id"]),
            "name": str(data["name"]),
            "lastname": str(data["lastname"]),
            "id_card": str(data["id_card"]),
            "phone": str(data["phone"])
        })

def save_trainer_to_db(data):
    """
    Save a trainer's data to the database.
    """
    with engine.begin() as connection:
        query = text("""
        INSERT INTO trainers (chat_id, name, lastname, id_card, phone)
        VALUES (:chat_id, :name, :lastname, :id_card, :phone)
        ON CONFLICT (chat_id) DO UPDATE
        SET 
            name = EXCLUDED.name,
            lastname = EXCLUDED.lastname,
            id_card = EXCLUDED.id_card,
            phone = EXCLUDED.phone;
        """)
        connection.execute(query, {
            "chat_id": str(data["chat_id"]),
            "name": str(data["name"]),
            "lastname": str(data["lastname"]),
            "id_card": str(data["id_card"]),
            "phone": str(data["phone"])
        })

def get_role(chat_id):
    """
    Get the role of a user by chat_id.
    """
    with engine.begin() as connection:
        query = text("SELECT role FROM users WHERE chat_id = :chat_id;")
        result = connection.execute(query, {"chat_id": str(chat_id)})
        result = result.fetchone()
        return result[0] if result else None

def get_payment_date(chat_id):
    """
    Get the payment date of a client by chat_id.
    """
    try:
        with engine.begin() as connection:
            query = text("SELECT init_date FROM clients WHERE chat_id = :chat_id;")
            result = connection.execute(query, {"chat_id": str(chat_id)})
            result = result.fetchone()
            return result[0] if result else None
    except Exception as e:
        return e

def check_user(chat_id):
    """
    Check if a user exists in the database by chat_id.
    """
    with engine.begin() as connection:
        query = text("SELECT EXISTS (SELECT 1 FROM progress WHERE chat_id = :chat_id);")
        result = connection.execute(query, {"chat_id": str(chat_id)})
        result = result.fetchone()
        return result[0]
    
def save_progress(data):
    # Guardar en la base de datos
    with engine.begin() as connection:
        query = text("""
            INSERT INTO progress (chat_id, weight, height, age, imc, corporal_fat, measure_date)
            VALUES (:chat_id, :weight, :height, :age, :bmi, :body_fat, :measure_date)
        """)
        connection.execute(query, {
            "chat_id": data["chat_id"],
            "weight": data["weight"],
            "height": data["height"],
            "age": data["age"],
            "bmi": round(data["bmi"], 2),
            "body_fat": round(data["body_fat"], 2),
            "measure_date": datetime.now().strftime('%Y-%m-%d')
        })

def last_progress(chat_id):
    # Obtener el último registro de progreso
    with engine.begin() as connection:
        query = text("SELECT * FROM progress WHERE chat_id = :chat_id ORDER BY measure_date DESC LIMIT 1;")
        result = connection.execute(query, {"chat_id": str(chat_id)})
        result = result.fetchone()
        return result

def get_user_data(chat_id):
    """
    Get the user data of a client by chat_id.
    """
    try:
        with engine.begin() as connection:
            query = text("SELECT gender, id_card FROM clients WHERE chat_id = :chat_id;")
            result = connection.execute(query, {"chat_id": str(chat_id)})
            result = result.fetchone()
            return result if result else None
    except Exception as e:
        return e