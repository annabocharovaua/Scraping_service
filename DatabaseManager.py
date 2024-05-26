import mysql.connector
from threading import Lock

class DatabaseManager:
    def __init__(self, config):
        self.config = config
        self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="my_pool",
            pool_size=5,
            **config
        )
        self.query_lock = Lock()

    def get_connection(self):
        return self.connection_pool.get_connection()

    def execute_query(self, query, params=None):
       with self.query_lock:
          connection = self.get_connection()
          cursor = connection.cursor()
          try:
              if params:
                  cursor.execute(query, params)
              else:
                  cursor.execute(query)

              if query.strip().upper().startswith('SELECT'):
                  results = cursor.fetchall()
              else:
                  connection.commit()
                  results = []

          except Exception as e:
              print(f"Помилка при виконанні запросу: {e}")
              results = None

          cursor.close()
          connection.close()
          return results

    def get_requests_from_db(self):
        query = """
            SELECT * FROM requests
            """
        return self.execute_query(query)