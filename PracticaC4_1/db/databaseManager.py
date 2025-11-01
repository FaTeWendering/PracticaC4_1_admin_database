import mysql.connector
from mysql.connector import Error


class DatabaseManager:

    def __init__(self, host, database, user, password):
        self.connection = None
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connect()

    def connect(self):
        """Establece la conexión con la base de datos."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("Conexión exitosa a MariaDB")
        except Error as e:
            print(f"Error al conectar con MariaDB: {e}")
            self.connection = None

    def validar_usuario(self, login, password):
        if not self.connection or not self.connection.is_connected():
            return None  # Error de conexión

        cursor = self.connection.cursor()
        query = """
            SELECT
                u.CvUser, u.EdoCta, u.FecIni, u.FecVen,
                n.DsNombre, 
                ap.DsApellid, 
                am.DsApellid,
                p.DsPuesto,
                g.DsGenero
            FROM
                mUsuario u
            JOIN mDtsPerson dp ON u.CvPerson = dp.CvPerson
            JOIN cNombre n ON dp.CvNombre = n.CvNombre
            JOIN cApellid ap ON dp.CvApePat = ap.CvApellid
            JOIN cApellid am ON dp.CvApeMat = am.CvApellid
            LEFT JOIN cPuesto p ON dp.CvPuesto = p.CvPuesto
            LEFT JOIN cGenero g ON dp.CvGenero = g.CvGenero
            WHERE
                u.Login = %s AND u.Password = %s;
        """

        try:
            cursor.execute(query, (login, password))
            resultado = cursor.fetchone()

            if resultado is None:
                return -1

            return resultado

        except Error as e:
            print(f"ERROR EN LA CONSULTA DE VALIDACIÓN: {e}")
            return None
        finally:
            cursor.close()

    def actualizar_estado_cuenta(self, cv_user, nuevo_estado):
        if not self.connection or not self.connection.is_connected():
            print("Error: No hay conexión a la base de datos.")
            return False

        cursor = self.connection.cursor()
        query = """
            UPDATE mUsuario
            SET EdoCta = %s
            WHERE CvUser = %s;
        """
        try:
            cursor.execute(query, (nuevo_estado, cv_user))

            self.connection.commit()

            if cursor.rowcount > 0:
                print(f"Estado actualizado para CvUser {cv_user} a '{nuevo_estado}'")
                return True
            else:
                print(f"No se encontró el CvUser {cv_user} para actualizar.")
                return False

        except Error as e:
            print(f"ERROR AL ACTUALIZAR: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

