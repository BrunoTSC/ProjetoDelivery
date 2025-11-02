import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",       # ajuste se precisar
        user="root",            # seu usuário
        password="P@lmeiras1914",   # sua senha
        database="delivery_db"
    )
    return conn
