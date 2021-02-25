import psycopg2

conn = psycopg2.connect(dbname="postgres",
                        user="postgres",
                        password="postgres",
                        host="db")
domains = ["zaceny",
               "doehalo",
               "godnoten",
               "aloauto",
               "ali_do_3",
               "ali_stallions",
               "ali_yourcars",
               "s_stylist",
               "asianstyleali",
               "alie_kids",
               "instryment_s_kitay"]
print("11111111111111111111111111111111")
cur = conn.cursor()


cur.execute("DROP TABLE IF EXISTS products")

cur.execute("CREATE TABLE products (id SERIAL PRIMARY KEY, text VARCHAR);")

for domain in domains:
    cur.execute("INSERT INTO products (text) VALUES(%s)", (domain,))

cur.execute("SELECT * FROM products;")

print(cur.fetchall())
conn.commit()
cur.close()

conn.close()
