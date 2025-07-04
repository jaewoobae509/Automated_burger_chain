import mysql.connector
from credentials import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


def get_db_connection():
    """Establishes and returns a MySQL database connection."""
    try:
        mydb = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return mydb
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def close_db_connection(mydb):
    """Closes a MySQL database connection."""
    if mydb and mydb.is_connected():
        mydb.close()
        print("Database connection closed.")

def get_db_cursor(mydb):
    """Returns a database cursor from the given connection."""
    if mydb:
        return mydb.cursor()
    return None

