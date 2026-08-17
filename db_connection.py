# db_connection.py
import pyodbc
import threading


class DatabaseConnection:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.connection = None
        self._local = threading.local()
        self._connect_lock = threading.Lock()

    def _get_thread_connection(self):
        return getattr(self._local, 'connection', None)

    def _set_thread_connection(self, conn):
        self._local.connection = conn
        # Backward compatibility: some callers may still inspect this attribute.
        self.connection = conn

    def _close_connection_safely(self, conn):
        if not conn:
            return
        try:
            conn.close()
        except Exception:
            pass

    def _is_connection_alive(self, conn):
        """Verifica in modo leggero che la connessione sia ancora utilizzabile."""
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return True
        except pyodbc.Error:
            return False
        except Exception:
            return False

    def _build_connection_string(self):
        config = self.config_manager.load_config()

        drivers = [
            'ODBC Driver 18 for SQL Server',
            'ODBC Driver 17 for SQL Server',
            'SQL Server',
            'SQL Server Native Client 11.0'
        ]

        driver = None
        available_drivers = pyodbc.drivers()
        for d in drivers:
            if d in available_drivers:
                driver = d
                break

        if driver is None:
            raise Exception("Nessun driver SQL Server trovato. Installa un driver ODBC per SQL Server.")

        return (
            f"DRIVER={{{driver}}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"UID={config['username']};"
            f"PWD={config['password']};"
            "Trusted_Connection=no;"
            "TrustServerCertificate=yes;"
            "Encrypt=yes;"
            "Connection Timeout=8;"
            "ConnectRetryCount=1;"
            "ConnectRetryInterval=5;"
            "Mars_Connection=yes;"
        )

    def _create_new_connection(self):
        conn_str = self._build_connection_string()
        conn = pyodbc.connect(conn_str, timeout=8)
        conn.autocommit = True
        conn.timeout = 15  # timeout per ogni singola query (secondi)
        return conn

    def connect(self):
        """Crea una connessione al database usando le credenziali crittografate"""
        existing_conn = self._get_thread_connection()
        if self._is_connection_alive(existing_conn):
            return existing_conn

        # Evita riconnessioni concorrenti nello stesso processo.
        with self._connect_lock:
            existing_conn = self._get_thread_connection()
            if self._is_connection_alive(existing_conn):
                return existing_conn

            self._close_connection_safely(existing_conn)
        try:
            new_conn = self._create_new_connection()
            self._set_thread_connection(new_conn)
            print("Connessione stabilita con successo!")
            return new_conn
        except pyodbc.Error as e:
            print(f"Errore durante la connessione: {str(e)}")
            raise

    def disconnect(self):
        """Chiude la connessione al database"""
        try:
            conn = self._get_thread_connection()
            self._close_connection_safely(conn)
            self._set_thread_connection(None)
        except Exception as e:
            print(f"Errore durante la chiusura della connessione: {str(e)}")

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
