import os
from sqlalchemy import create_engine, text

# Fetch the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set. Make sure it's configured in your Railway project.")

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
        connection.execute(query, {"chat_id": data["chat_id"], "role": data["role"]})

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
            "chat_id": data["chat_id"],
            "name": data["name"],
            "lastname": data["lastname"],
            "gender": data["gender"],
            "id_card": data["id_card"],
            "phone": data["phone"],
            "membership": data["membership"],
            "init_date": data["init_date"]
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
            "chat_id": data["chat_id"],
            "name": data["name"],
            "lastname": data["lastname"],
            "id_card": data["id_card"],
            "phone": data["phone"]
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
            "chat_id": data["chat_id"],
            "name": data["name"],
            "lastname": data["lastname"],
            "id_card": data["id_card"],
            "phone": data["phone"]
        })

def get_role(chat_id):
    """
    Get the role of a user by chat_id.
    """
    with engine.begin() as connection:
        query = text("SELECT role FROM users WHERE chat_id = :chat_id;")
        result = connection.execute(query, {"chat_id": chat_id}).fetchone()
        return result["role"] if result else None

def get_payment_date(chat_id):
    """
    Get the payment date of a client by chat_id.
    """
    with engine.begin() as connection:
        query = text("SELECT init_date FROM clients WHERE chat_id = :chat_id;")
        result = connection.execute(query, {"chat_id": chat_id}).fetchone()
        return result["init_date"] if result else None

# Example Usage
if __name__ == "__main__":
    initialize_db()

    # Save a user
    save_user({"chat_id": "12345", "role": "admin"})

    # Retrieve the user's role
    role = get_role("12345")
    print(f"User's role: {role}")

    # Save a client
    save_client_to_db({
        "chat_id": "67890",
        "name": "John",
        "lastname": "Doe",
        "gender": "Male",
        "id_card": "12345678901",
        "phone": "12345678",
        "membership": "CrossFit",
        "init_date": "2025-01-26",
    })

    # Retrieve a client's payment date
    payment_date = get_payment_date("67890")
    print(f"Client's payment date: {payment_date}")
