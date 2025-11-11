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
                password=self.password,
                autocommit=True
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

    # --- FUNCIONES PARA MÓDULO DE PERSONAS ---

    def _get_catalog_data(self, query):
        """Función auxiliar genérica para leer catálogos simples."""
        if not self.connection or not self.connection.is_connected():
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error al obtener catálogo: {e}")
            return []
        finally:
            cursor.close()

    def get_generos(self):
        """Obtiene la lista de géneros (ID, Nombre) de cGenero."""
        query = "SELECT CvGenero, DsGenero FROM cGenero ORDER BY DsGenero"
        return self._get_catalog_data(query)

    def get_puestos(self):
        """Obtiene la lista de puestos (ID, Nombre) de cPuesto."""
        query = "SELECT CvPuesto, DsPuesto FROM cPuesto ORDER BY DsPuesto"
        return self._get_catalog_data(query)

    def get_tipos_persona(self):
        """Obtiene la lista de tipos de persona (ID, Nombre) de cTpPerso."""
        query = "SELECT CvTpPerson, DsTpPerson FROM cTpPerso ORDER BY DsTpPerson"
        return self._get_catalog_data(query)

    def get_all_personas_info(self):
        """
        Obtiene la información combinada de mDtsPerson y mUsuario
        para llenar la tabla de consulta.
        """
        if not self.connection or not self.connection.is_connected():
            return []

        query = """
                SELECT u.CvUser,
                       u.Login,
                       CONCAT(n.DsNombre, ' ', ap.DsApellid, ' ', am.DsApellid) AS NombreCompleto,
                       tp.DsTpPerson                                            AS Tipo,
                       p.DsPuesto                                               AS Puesto,
                       dp.E_mail,
                       dp.Telefono,
                       u.EdoCta
                FROM mUsuario u
                         JOIN mDtsPerson dp ON u.CvPerson = dp.CvPerson
                         JOIN cNombre n ON dp.CvNombre = n.CvNombre
                         JOIN cApellid ap ON dp.CvApePat = ap.CvApellid
                         JOIN cApellid am ON dp.CvApeMat = am.CvApellid
                         LEFT JOIN cTpPerso tp ON dp.CvTpPerso = tp.CvTpPerson
                         LEFT JOIN cPuesto p ON dp.CvPuesto = p.CvPuesto
                ORDER BY NombreCompleto;
                """
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        except Error as e:
            print(f"Error al obtener toda la info de personas: {e}")
            return []
        finally:
            cursor.close()

    def _get_or_create_catalog_id(self, cursor, tabla, pk_col, ds_col, valor_str):
        """
        Función auxiliar: Busca un string (ej. "Alan") en una tabla (ej. "cNombre").
        Si existe, devuelve su ID.
        Si no existe, lo inserta y devuelve el nuevo ID.
        """
        # 1. Buscar si el valor ya existe
        cursor.execute(f"SELECT {pk_col} FROM {tabla} WHERE {ds_col} = %s", (valor_str,))
        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]  # Devolver el ID existente
        else:
            # 2. Si no existe, insertarlo
            cursor.execute(f"INSERT INTO {tabla} ({ds_col}) VALUES (%s)", (valor_str,))
            return cursor.lastrowid  # Devolver el nuevo ID

    def check_login_exists(self, login, current_user_id=None):
        """
        Verifica si un login ya existe en mUsuario.
        Si 'current_user_id' se provee, excluye a ese usuario de la búsqueda (para 'Actualizar').
        """
        if not self.connection or not self.connection.is_connected():
            return True  # Asumir que existe si hay error de BD

        cursor = self.connection.cursor()
        try:
            if current_user_id:
                query = "SELECT CvUser FROM mUsuario WHERE Login = %s AND CvUser != %s;"
                cursor.execute(query, (login, current_user_id))
            else:
                query = "SELECT CvUser FROM mUsuario WHERE Login = %s;"
                cursor.execute(query, (login,))

            return cursor.fetchone() is not None  # True si encuentra algo

        except Error as e:
            print(f"Error al verificar login: {e}")
            return True  # Bloquear por seguridad
        finally:
            cursor.close()

    def add_persona_y_usuario(self, datos_persona, datos_usuario, admin_login):
        """
        Función transaccional para crear una Persona y un Usuario.
        'datos_persona' es un dict para mDtsPerson.
        'datos_usuario' es un dict para mUsuario.
        """
        if not self.connection or not self.connection.is_connected():
            return False

        cursor = self.connection.cursor()
        try:
            # ¡Iniciamos una transacción!
            self.connection.start_transaction()

            # 1. Obtener/Crear IDs de catálogos de nombres
            cv_nombre = self._get_or_create_catalog_id(cursor, "cNombre", "CvNombre", "DsNombre",
                                                       datos_persona['Nombre'])
            cv_apepat = self._get_or_create_catalog_id(cursor, "cApellid", "CvApellid", "DsApellid",
                                                       datos_persona['ApePat'])
            cv_apemat = self._get_or_create_catalog_id(cursor, "cApellid", "CvApellid", "DsApellid",
                                                       datos_persona['ApeMat'])

            # 2. Insertar en mDtsPerson
            # --- ¡ESTA ES LA PARTE CORREGIDA! ---
            query_person = """
                           INSERT INTO mDtsPerson
                           (CvNombre, CvApePat, CvApeMat, FecNac, E_mail, Telefono,
                            CvGenero, CvPuesto, CvTpPerso,
                            CvGdoAca, CvAficion, CvDirecc, CvDepto,
                            RedSoc, Edad) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 1, 1, 1, 1, %s, %s);
                           """
            # Se añadieron RedSoc y Edad a la consulta

            cursor.execute(query_person, (
                cv_nombre, cv_apepat, cv_apemat,
                datos_persona['FecNac'], datos_persona['E_mail'], datos_persona['Telefono'],
                datos_persona['CvGenero'], datos_persona['CvPuesto'], datos_persona['CvTpPerso'],
                datos_persona['RedSoc'], datos_persona['Edad'] # Se pasan los nuevos datos
            ))
            # --- FIN DE LA CORRECCIÓN ---

            # 3. Obtener el ID de la nueva persona
            cv_person_nuevo = cursor.lastrowid

            # 4. Insertar en mUsuario (Esta parte no cambia)
            query_user = """
                         INSERT INTO mUsuario
                             (CvPerson, Login, Password, FecIni, FecVen, EdoCta)
                         VALUES (%s, %s, %s, %s, %s, %s);
                         """
            cursor.execute(query_user, (
                cv_person_nuevo,
                datos_usuario['Login'], datos_usuario['Password'],
                datos_usuario['FecIni'], datos_usuario['FecVen'], datos_usuario['EdoCta']
            ))

            # 5. Confirmar todos los cambios
            self.connection.commit()

            # 6. Registrar en Bitácora
            detalle_evento = f"AUDITORIA BD: INSERT en mDtsPerson (ID: {cv_person_nuevo}) y mUsuario (Login: {datos_usuario['Login']})"
            self.registrar_acceso(admin_login, True, detalle_evento)

            return True

        except Error as e:
            print(f"Error en la transacción de añadir persona: {e}")
            self.connection.rollback()  # ¡Deshacer todo si algo falla!
            return False
        finally:
            cursor.close()

    def get_persona_info_by_id(self, cv_user):
        """
        Obtiene todos los datos de una persona/usuario específico para llenar el formulario de edición.
        """
        if not self.connection or not self.connection.is_connected():
            return None

        query = """
                SELECT dp.CvPerson,
                       n.DsNombre,
                       ap.DsApellid AS ApePat,
                       am.DsApellid AS ApeMat,
                       dp.FecNac, 
                       dp.E_mail,
                       dp.Telefono,
                       dp.CvGenero,
                       dp.CvPuesto,
                       dp.CvTpPerso,
                       u.Login,
                       u.Password,
                       u.FecIni,
                       u.FecVen,
                       u.EdoCta
                FROM mUsuario u
                         JOIN mDtsPerson dp ON u.CvPerson = dp.CvPerson
                         JOIN cNombre n ON dp.CvNombre = n.CvNombre
                         JOIN cApellid ap ON dp.CvApePat = ap.CvApellid
                         JOIN cApellid am ON dp.CvApeMat = am.CvApellid
                WHERE u.CvUser = %s;
                """
        cursor = self.connection.cursor(dictionary=True)  # <-- Usamos dictionary=True para obtener {col: val}
        try:
            cursor.execute(query, (cv_user,))
            return cursor.fetchone()  # Devuelve un diccionario con los resultados
        except Error as e:
            print(f"Error al obtener datos de la persona: {e}")
            return None
        finally:
            cursor.close()

    def update_persona_y_usuario(self, cv_user, cv_person, datos_persona, datos_usuario, admin_login):
        """
        Función transaccional para ACTUALIZAR una Persona y un Usuario.
        """
        if not self.connection or not self.connection.is_connected():
            return False

        cursor = self.connection.cursor()
        try:
            # ¡Iniciamos una transacción!
            self.connection.start_transaction()

            # 1. Obtener/Crear IDs de catálogos de nombres
            cv_nombre = self._get_or_create_catalog_id(cursor, "cNombre", "CvNombre", "DsNombre",
                                                       datos_persona['Nombre'])
            cv_apepat = self._get_or_create_catalog_id(cursor, "cApellid", "CvApellid", "DsApellid",
                                                       datos_persona['ApePat'])
            cv_apemat = self._get_or_create_catalog_id(cursor, "cApellid", "CvApellid", "DsApellid",
                                                       datos_persona['ApeMat'])

            # 2. Actualizar mDtsPerson
            query_person = """
                           UPDATE mDtsPerson
                           SET CvNombre  = %s,
                               CvApePat  = %s,
                               CvApeMat  = %s,
                               FecNac    = %s,
                               E_mail    = %s,
                               Telefono  = %s,
                               CvGenero  = %s,
                               CvPuesto  = %s,
                               CvTpPerso = %s,
                               Edad      = %s,
                               RedSoc    = %s
                           WHERE CvPerson = %s;
                           """
            cursor.execute(query_person, (
                cv_nombre, cv_apepat, cv_apemat,
                datos_persona['FecNac'], datos_persona['E_mail'], datos_persona['Telefono'],
                datos_persona['CvGenero'], datos_persona['CvPuesto'], datos_persona['CvTpPerso'],
                datos_persona['Edad'], datos_persona['RedSoc'],
                cv_person  # <-- ID de la persona a actualizar
            ))

            # 3. Actualizar mUsuario
            query_user = """
                         UPDATE mUsuario
                         SET Login    = %s,
                             Password = %s,
                             FecIni   = %s,
                             FecVen   = %s,
                             EdoCta   = %s
                         WHERE CvUser = %s;
                         """
            cursor.execute(query_user, (
                datos_usuario['Login'], datos_usuario['Password'],
                datos_usuario['FecIni'], datos_usuario['FecVen'], datos_usuario['EdoCta'],
                cv_user  # <-- ID del usuario a actualizar
            ))

            # 4. Confirmar todos los cambios
            self.connection.commit()

            # 5. Registrar en Bitácora
            detalle_evento = f"AUDITORIA BD: UPDATE en mDtsPerson (ID: {cv_person}) y mUsuario (ID: {cv_user})"
            self.registrar_acceso(admin_login, True, detalle_evento)

            return True

        except Error as e:
            print(f"Error en la transacción de actualizar persona: {e}")
            self.connection.rollback()  # ¡Deshacer todo si algo falla!
            return False
        finally:
            cursor.close()

            
