import mysql.connector
import os

# Function to connect to the database
def connect_db():
    try:
        #print("Attempting to connect to the database...")
        conn = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"],
            database=os.environ["DB_NAME"]
        )
        #print("Connected to the database successfully!")
        return conn
    except mysql.connector.Error as e:
        print(f"Database connection failed: {e}")
        return None
