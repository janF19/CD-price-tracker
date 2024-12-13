import psycopg2
from psycopg2 import sql

# Connection details
db_url = "postgresql://trains_price_database_user:rGPZc73zwHGbSJPSq3stWtKhxMBszGaL@dpg-cta4bvogph6c73ek0ve0-a.frankfurt-postgres.render.com/trains_price_database"

# Connect to the PostgreSQL database
conn = psycopg2.connect(db_url)
cur = conn.cursor()

# Query to truncate the table (replace 'train_data' with the correct table name)
table_name = 'train_connections'  # Replace with the actual table name
cur.execute(sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY CASCADE;").format(sql.Identifier(table_name)))

# Commit changes and close the connection
conn.commit()
cur.close()
conn.close()

print("Data cleared successfully!")

