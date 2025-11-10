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

    def registrar_acceso(self, usuario_intento, exito, detalle_evento):
        if not self.connection or not self.connection.is_connected():
            print("Error no hay conexion en la base de datos para la bitacora.")
            return False

        cursor = self.connection.cursor()

        query = """
        INSERT INTO bitacora_accesos
            (usuario_intento, fecha_hora, exito, detalle_evento)
        VALUES
            (%s, NOW(), %s, %s);"""

        try:
            datos = (usuario_intento, exito, detalle_evento)
            cursor.execute(query, datos)

            self.connection.commit()
            print(f"Registro en la bitacora guardado: {usuario_intento}, {detalle_evento}")
            return True
        except Error as e:
            print(f"Error en mostrar en bitacora: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def verificar_password_existente(self, nuevo_password):
        """
        Verifica si un password ya existe en la tabla mUsuario.
        Retorna True si existe, False si no existe.
        """
        if not self.connection or not self.connection.is_connected():
            return True  # Por seguridad, si no hay BD, no dejamos cambiar

        cursor = self.connection.cursor()
        query = "SELECT CvUser FROM mUsuario WHERE Password = %s;"

        try:
            cursor.execute(query, (nuevo_password,))
            resultado = cursor.fetchone()

            # Si fetchone() encuentra algo (no es None), significa que SÍ existe
            return resultado is not None

        except Error as e:
            print(f"ERROR AL VERIFICAR PASSWORD: {e}")
            return True  # Por seguridad, bloqueamos el cambio
        finally:
            cursor.close()

    def actualizar_password(self, login_usuario, nuevo_password):
        """
        Actualiza la contraseña de un usuario específico Y REGISTRA EN BITACORA.
        """
        if not self.connection or not self.connection.is_connected():
            print("Error: No hay conexión a la base de datos.")
            return False

        cursor = self.connection.cursor()
        query = """
            UPDATE mUsuario
            SET Password = %s
            WHERE Login = %s;
        """
        try:
            cursor.execute(query, (nuevo_password, login_usuario))
            self.connection.commit()

            # --- INICIO DE AUDITORÍA DE SEGURIDAD ---
            detalle_evento = "AUDITORIA SEGURIDAD: Cambio de contraseña exitoso."
            self.registrar_acceso(login_usuario, True, detalle_evento)
            # --- FIN DE AUDITORÍA ---

            return cursor.rowcount > 0  # Retorna True si la fila fue actualizada

        except Error as e:
            print(f"ERROR AL ACTUALIZAR PASSWORD: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    #Pagos
    def get_pagos_por_usuario(self, cv_user):
        """Obtiene todos los pagos de un usuario específico (para Alumnos)"""
        if not self.connection or not self.connection.is_connected():
            return []

        query = """
        SELECT 
            f.CvCobro, f.FechaCobro, f.Tipo, f.Monto, f.Descuento, f.Estado,
            CONCAT(n.DsNombre, ' ', ap.DsApellid) AS NombreAlumno
        FROM fCobro f
        JOIN mUsuario u ON f.CvUsuario = u.CvUser
        JOIN mDtsPerson dp ON u.CvPerson = dp.CvPerson
        JOIN cNombre n ON dp.CvNombre = n.CvNombre
        JOIN cApellid ap ON dp.CvApePat = ap.CvApellid
        WHERE f.CvUsuario = %s
        ORDER BY f.FechaCobro DESC;
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (cv_user))
            return cursor.fetchall()
        except Error as e:
            print(f"Error al obtener pagos por usuario: {e}")
            return []
        finally:
            cursor.close()

    def get_todos_los_pagos(self):
        """Obtine todos los pagos (para Directores/Admin)"""
        if not self.connection or not self.connection.is_connected():
            return []
        query = """
        SELECT 
            f.CvCobro, f.FechaCobro, f.Tipo, f.Monto, f.Descuento, f.Estado,
            CONCAT(n.DsNombre, ' ', ap.DsApellid) AS NombreAlumno,
            f.CvUsuario
        FROM fCobro f
        JOIN mUsuario u ON f.CvUsuario = u.CvUser
        JOIN mDtsPerson dp ON u.CvPerson = dp.CvPerson
        JOIN cNombre n ON dp.CvNombre = n.CvNombre
        JOIN cApellid ap ON dp.CvApePat = ap.CvApellid
        ORDER BY f.FechaCobro DESC;
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error al obtener todos los pagos: {e}")
            return []
        finally:
            cursor.close()

    def get_alumnos_para_combobox(self):
        """Obtiene todos los alumnos (ID, Nombre) para llenar el combobox"""
        if not self.connection or not self.connection.is_connected():
            return []
        query = """
            SELECT 
            u.CvUser,
            CONCAT(n.DsNombre, ' ', ap.DsApellid, ' ', am.DsApellid) AS NombreCompleto
        FROM mUsuario u
        JOIN mDtsPerson dp ON u.CvPerson = dp.CvPerson
        JOIN cTpPerso tp ON dp.CvTpPerso = tp.CvTpPerson
        JOIN cNombre n ON dp.CvNombre = n.CvNombre
        JOIN cApellid ap ON dp.CvApePat = ap.CvApellid
        JOIN cApellid am ON dp.CvApeMat = am.CvApellid
        WHERE tp.DsTpPerson = 'Alumno'
        ORDER BY NombreCompleto;
        """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error al obtener la lista de alumnos: {e}")
            return []
        finally:
            cursor.close()

    def add_pago(self, cv_usuario, fecha, tipo, monto, descuento, estado, admin_login):
        """Insertar un nuevo registro de pago en fCobro Y REGISTRA EN BITACORA."""
        if not self.connection or not self.connection.is_connected():
            return False
        query = """
                INSERT INTO fCobro (CvUsuario, FechaCobro, Tipo, Monto, Descuento, Estado)
                VALUES (%s, %s, %s, %s, %s, %s); \
                """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (cv_usuario, fecha, tipo, monto, descuento, estado))
            self.connection.commit()

            # --- INICIO DE AUDITORÍA ---
            # Obtenemos el ID del pago que acabamos de insertar
            nuevo_pago_id = cursor.lastrowid
            detalle_evento = f"AUDITORIA BD: INSERT en fCobro. ID: {nuevo_pago_id}, Alumno ID: {cv_usuario}"
            self.registrar_acceso(admin_login, True, detalle_evento)
            # --- FIN DE AUDITORÍA ---

            return True
        except Error as e:
            print(f"Error al añadir pago {e}")
            self.connection.rollback()  # <--- ¡IMPORTANTE! Asegúrate de tener rollback aquí
            return False
        finally:
            cursor.close()

    def get_tipos_pago(self):
        """Obtiene todos los tipos de pago (ID, Nombre, Monto) para el ComboBox."""
        if not self.connection or not self.connection.is_connected():
            return []

        query = "SELECT CvTipoPago, DsTipoPago, Monto FROM cTiposPago ORDER BY DsTipoPago;"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error al obtener tipos de pago: {e}")
            return []
        finally:
            cursor.close()

    def get_descuentos(self):
        """Obtiene todos los descuentos (ID, Nombre, Porcentaje) para el ComboBox."""
        if not self.connection or not self.connection.is_connected():
            return []

        query = "SELECT CvDescuento, DsDescuento, Porcentaje FROM cDescuentos ORDER BY Porcentaje;"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error al obtener descuentos: {e}")
            return []
        finally:
            cursor.close()

    def update_pago(self, cv_cobro, cv_usuario, fecha, tipo, monto, descuento, estado, admin_login):
        """Actualiza un registro de pago existente en fCobro Y REGISTRA EN BITACORA."""
        if not self.connection or not self.connection.is_connected():
            return False

        query = """
                UPDATE fCobro
                SET CvUsuario  = %s,
                    FechaCobro = %s,
                    Tipo       = %s,
                    Monto      = %s,
                    Descuento  = %s,
                    Estado     = %s
                WHERE CvCobro = %s;
                """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (cv_usuario, fecha, tipo, monto, descuento, estado, cv_cobro))
            self.connection.commit()

            # --- INICIO DE AUDITORÍA ---
            detalle_evento = f"AUDITORIA BD: UPDATE en fCobro. ID: {cv_cobro}"
            self.registrar_acceso(admin_login, True, detalle_evento)
            # --- FIN DE AUDITORÍA ---

            return True
        except Error as e:
            print(f"Error al actualizar pago: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()

    def delete_pago(self, cv_cobro, admin_login):
        """Elimina un registro de pago de fCobro Y REGISTRA EN BITACORA."""
        if not self.connection or not self.connection.is_connected():
            return False

        query = "DELETE FROM fCobro WHERE CvCobro = %s;"
        cursor = self.connection.cursor()
        try:
            cursor.execute(query, (cv_cobro,))
            self.connection.commit()

            # --- INICIO DE AUDITORÍA ---
            detalle_evento = f"AUDITORIA BD: DELETE en fCobro. ID: {cv_cobro}"
            self.registrar_acceso(admin_login, True, detalle_evento)
            # --- FIN DE AUDITORÍA ---

            return True
        except Error as e:
            print(f"Error al eliminar pago: {e}")
            self.connection.rollback()
            return False
        finally:
            cursor.close()


            
