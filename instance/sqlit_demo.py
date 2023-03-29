import sqlite3

# This file is created in the instance folder
# It's purpose is to view the database

conn = sqlite3.connect('database.db')
c = conn.cursor()

c.execute("SELECT email from User")

print(c.fetchall())

conn.close()