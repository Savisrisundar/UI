import psycopg2

# Replace the placeholders with your CockroachDB connection details
conn = psycopg2.connect(
    host="dpg-cm4gb4i1hbls73ademp0-a.singapore-postgres.render.com",
    port=5432,
    user="vitcc",
    password="BIY9sFDKjt33V4LdTOdRK7nzlSkTg8QW",
    database="libraryvit"
)



# Create a cursor object to interact with the database
cur = conn.cursor()

cur.execute("SELECT table_name FROM information_schema.tables;")
x = cur.fetchall()

print('_____________________________________________________________')
query = f"SELECT column_name FROM information_schema.columns WHERE table_name = 'Availability';"
cur.execute(query)
x1 = cur.fetchall()
for i in x1:
    print(i)

cur.execute("SELECT  * from Availability;")
x = cur.fetchall()
for i in x:
    print(i)


cur.close()
conn.close()
