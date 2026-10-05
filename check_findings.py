import sqlite3

conn = sqlite3.connect("recon.db")
cur = conn.cursor()

cur.execute("SELECT * FROM findings")

for row in cur.fetchall():
    print(row)

conn.close()