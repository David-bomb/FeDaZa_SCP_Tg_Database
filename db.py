import sqlite3
# Этот файл нужен для переписывания базы данных пользователей в случае нужны
conn = sqlite3.connect('users.db')
cur = conn.cursor()
'''cur.execute("""CREATE TABLE IF NOT EXISTS users( 
   userid INT PRIMARY KEY,
   name TEXT,
   level INTEGER,
   number_of_requests INTEGER);
""")'''
check = cur.execute('''SELECT * FROM users''').fetchall()
print(check)
