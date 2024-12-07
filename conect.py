import psycopg2
from urllib.parse import urlparse
import traceback

def connect_to_database(database_url):
    """
    Establish a connection to the PostgreSQL database
    
    Args:
        database_url (str): PostgreSQL connection URL
    
    Returns:
        tuple: (connection object, error message)
    """
    try:
        # Parse the database URL
        url_parts = urlparse(database_url)
        
        # Construct connection parameters
        conn_params = {
            'dbname': url_parts.path.lstrip('/'),
            'user': url_parts.username,
            'password': url_parts.password,
            'host': url_parts.hostname,
            'port': url_parts.port or 5432,
            'client_encoding': 'utf8'  # Use UTF-8 encoding
        }
        
        # Attempt to connect
        conn = psycopg2.connect(**conn_params)
        
        return conn, None
    
    except psycopg2.Error as e:
        error_message = f"Database Connection Error: {e}"
        print(error_message)
        print(traceback.format_exc())
        return None, error_message

def execute_query(conn, query):
    """
    Execute a SQL query
    
    Args:
        conn (psycopg2.extensions.connection): Database connection
        query (str): SQL query to execute
    
    Returns:
        list: Query results
    """
    if not conn:
        print("No active database connection")
        return None
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
            return results
    except psycopg2.Error as e:
        print(f"Query Execution Error: {e}")
        return None

# Example usage
def main():
    # Replace with your actual database URL
    DATABASE_URL = "postgresql://trains_price_database_user:rGPZc73zwHGbSJPSq3stWtKhxMBszGaL@dpg-cta4bvogph6c73ek0ve0-a.frankfurt-postgres.render.com/trains_price_database"
    
    # Attempt to connect
    connection, error = connect_to_database(DATABASE_URL)
    
    if connection:
        print("✅ Successfully connected to the database")
        
        # Example query
        test_query = "SELECT 1"
        results = execute_query(connection, test_query)
        
        if results is not None:
            print(f"Query results: {results}")
        
        # Always close the connection
        connection.close()
    else:
        print("❌ Failed to connect to the database")
        print(f"Error details: {error}")

if __name__ == "__main__":
    main()