import sqlite3

# Этот файл нужен для переписывания базы данных пользователей в случае нужды
conn = sqlite3.connect('users.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS users( 
   userid INT PRIMARY KEY,
   username TEXT,
   name TEXT,
   level INTEGER,
   number_of_requests INTEGER,
   number_of_bugs INTEGER,
   date_of_registration DATETIME,
   photo TEXT,
   nickname TEXT,
   language TEXT,
   last_scp INTEGER)
""")
