import re
from PyQt6.QtCore import (
    Qt, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup
)
from PyQt6.QtGui import QMouseEvent, QIcon, QDoubleValidator
from PyQt6.QtWidgets import QDialog, QHeaderView, QLineEdit, QMessageBox, QTableWidgetItem, QAbstractItemView
from PyQt6.QtCore import QDate, QLocale
from .ui_ControlWindows import Ui_Dialog


class ControlWindows(QDialog):
    sesion_cerrada = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()

        self.db_manager = db_manager
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # Propiedades para guardar los datos del usuario actual
        self.current_login = None
        self.current_password = None
        self.current_puesto = None
        self.current_cv_user = None
        self.current_nombre_completo = None

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # --- ESTILOS PARA VALIDACIÓN (PASSWORD) ---

        # Estilo para QLineEdit (Campos de texto)
        self.style_qline_ok = """
            font-size: 10pt; color: white;
            background-color: #000000ff;
            border: 1px solid rgb(20, 200, 220);
            border-radius: 5px; padding: 4px;
        """
        self.style_qline_error = """
            font-size: 10pt; color: red;
            background-color: #000000ff;
            border: 1px solid red;
            border-radius: 5px; padding: 4px;
        """

        # Estilo para QLabel (Etiquetas de criterio)
        # (Usamos el estilo de la hoja de estilos de la página 7)
        self.style_crit_ok = "color: white;"  # O un verde claro: "color: rgb(0, 255, 0);"
        self.style_crit_error = "color: red;"

        # --- CONFIGURACIÓN DE BOTONES DE OJO (CAMBIAR PASS) ---
        try:
            # Reusa la ruta del ícono de LoginWindows
            ruta_icono = "Imagenes/eye_on_see_show_view_vision_watch_icon_123215.png"
            eye_icono = QIcon(ruta_icono)

            # Conectamos las señales 'textChanged' para la validación en vivo
            self.ui.txt_pass_nuevo.textChanged.connect(self.validar_password_nuevo)
            self.ui.txt_pass_repetir.textChanged.connect(self.validar_password_repetido)

            self.ui.txt_pass_anterior.setEchoMode(QLineEdit.EchoMode.Password)
            eye_action_anterior = self.ui.txt_pass_anterior.addAction(eye_icono,
                                                                      QLineEdit.ActionPosition.TrailingPosition)
            eye_action_anterior.triggered.connect(
                lambda: self.toggle_password_visibility(self.ui.txt_pass_anterior)
            )

            self.ui.txt_pass_nuevo.setEchoMode(QLineEdit.EchoMode.Password)
            eye_action_nuevo = self.ui.txt_pass_nuevo.addAction(eye_icono, QLineEdit.ActionPosition.TrailingPosition)
            eye_action_nuevo.triggered.connect(
                lambda: self.toggle_password_visibility(self.ui.txt_pass_nuevo)
            )

            self.ui.txt_pass_repetir.setEchoMode(QLineEdit.EchoMode.Password)
            eye_action_repetir = self.ui.txt_pass_repetir.addAction(eye_icono,
                                                                    QLineEdit.ActionPosition.TrailingPosition)
            eye_action_repetir.triggered.connect(
                lambda: self.toggle_password_visibility(self.ui.txt_pass_repetir)
            )
        except AttributeError as e:
            print(
                f"ADVERTENCIA (Botones Ojo/Validación): No se pudieron crear los botones/conectar señales. ¿Regeneraste el UI? Error: {e}")
        except Exception as e:
            print(f"Error inesperado configurando botones de ojo: {e}")

        # --- ESTADO INICIAL DE MÓDULOS ---
        self.estado_compras = "navegando"
        self.estado_actual_pagos = "consultando"

        # --- ANIMACIÓN MENÚ PRINCIPAL ---
        self.menu_ancho_desplegado = 220
        self.menu_esta_oculto = False
        self.animacion_grupo_main = None
        self.ui.frame_4.setMinimumWidth(self.menu_ancho_desplegado)
        self.ui.frame_4.setMaximumWidth(self.menu_ancho_desplegado)

        # --- ANIMACIÓN MENÚ COMPRAS ---
        self.compras_menu_ancho = 180
        self.compras_menu_oculto = False
        self.animacion_grupo_compras = None

        # --- CONEXIONES DE BOTONES DE LA VENTANA ---
        self.ui.btn_cerrar.clicked.connect(self.close)
        self.ui.btn_minimizar.clicked.connect(self.showMinimized)
        self.ui.btn_maximizar.clicked.connect(self.Maximizar)
        self.ui.btn_toggle_menu.clicked.connect(self.toggle_menu_main)
        self.ui.btn_toggle_menu.setText("<")

        # --- CONEXIONES DE BOTONES DEL MENÚ PRINCIPAL ---
        self.ui.pushButton_4.clicked.connect(self.mostrar_pagina_cambiarpass)
        self.ui.btn_cerrarsesion.clicked.connect(self.cerrar_sesion)

        try:
            self.ui.btn_pagos.clicked.connect(self.mostrar_pagina_pagos)
        except AttributeError as e:
            print(f"ADVERTENCIA: No se encontró el botón 'btn_pagos' en el menú. {e}")

        self.dragging = False
        self.offset = None

        # --- CONEXIONES DEL MÓDULO DE PAGOS ---
        try:
            # Conexiones de los botones de acción (CRUD)
            self.ui.btn_pagos_nuevo.clicked.connect(self.accion_pagos_nuevo)
            self.ui.btn_pagos_actualizar.clicked.connect(self.accion_pagos_actualizar)
            self.ui.btn_pagos_borrar.clicked.connect(self.accion_pagos_borrar)
            self.ui.btn_pagos_consultar.clicked.connect(self.accion_pagos_consultar)
            self.ui.btn_pagos_cancelar.clicked.connect(self.accion_pagos_cancelar)
            self.ui.btn_pagos_regresar.clicked.connect(self.accion_pagos_regresar)

            # Conectar señales de los ComboBox
            self.ui.combo_pagos_tipo.currentIndexChanged.connect(self.actualizar_monto_y_total)
            self.ui.combo_pagos_descuento.currentIndexChanged.connect(self.actualizar_monto_y_total)

            # Poner validadores a los campos de dinero (para que muestren $0.00)
            locale = QLocale(QLocale.Language.Spanish, QLocale.Country.Mexico)
            validator = QDoubleValidator(0.0, 99999.99, 2)
            validator.setLocale(locale)
            validator.setNotation(QDoubleValidator.Notation.StandardNotation)

            self.ui.txt_pagos_monto.setValidator(validator)
            self.ui.txt_pagos_total.setValidator(validator)

        except AttributeError as e:
            print(f"ADVERTENCIA: No se pudieron conectar los widgets de Pagos. ¿Regeneraste el UI? Error: {e}")

    # --- MÓDULO: NAVEGACIÓN DE PÁGINAS ---
    def mostrar_pagina_pagos(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.Pagos)

            self.cargar_tabla_pagos()

            self.cargar_combobox_alumnos()

            self.cargar_combobox_pagos_y_descuentos()

            if not self.menu_esta_oculto:
                self.toggle_menu_main()

            self.accion_pagos_consultar()
        except AttributeError as e:
            print(e)

    def mostrar_pagina_cambiarpass(self):
        try:
            # Asumiendo que se llama 'page_7'
            self.ui.stackedWidget.setCurrentWidget(self.ui.Cambiarpass)
            self.limpiar_campos_password()

            try:
                self.ui.btn_aceptar_pass.clicked.disconnect()
                self.ui.btn_cancel_pass.clicked.disconnect()
            except TypeError:
                pass

            self.ui.btn_aceptar_pass.clicked.connect(self.procesar_cambio_password)
            self.ui.btn_cancel_pass.clicked.connect(self.limpiar_campos_password)
        except AttributeError as e:
            print(f"Error: La pagina (CambiarPass) no existe. creela en Qt Designer. {e}")

    # --- MÓDULO: ANIMACIONES DE MENÚS ---

    def toggle_menu_main(self):
        if self.animacion_grupo_main and self.animacion_grupo_main.state() == QParallelAnimationGroup.State.Running:
            return

        ancho_fin = 0
        if self.menu_esta_oculto:
            ancho_fin = self.menu_ancho_desplegado
            self.ui.btn_toggle_menu.setText("<")
            self.menu_esta_oculto = False
        else:
            self.ui.btn_toggle_menu.setText("☰")
            self.menu_esta_oculto = True

        self.animacion_min = QPropertyAnimation(self.ui.frame_4, b"minimumWidth")
        self.animacion_max = QPropertyAnimation(self.ui.frame_4, b"maximumWidth")
        self.animacion_min.setDuration(300)
        self.animacion_min.setEndValue(ancho_fin)
        self.animacion_min.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animacion_max.setDuration(300)
        self.animacion_max.setEndValue(ancho_fin)
        self.animacion_max.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.animacion_grupo_main = QParallelAnimationGroup()
        self.animacion_grupo_main.addAnimation(self.animacion_min)
        self.animacion_grupo_main.addAnimation(self.animacion_max)
        self.animacion_grupo_main.start()

    # --- MÉTODOS BÁSICOS DE LA VENTANA ---

    def Maximizar(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.ui.frame_2.underMouse():
                self.dragging = True
                self.offset = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.move(self.mapToGlobal(event.pos() - self.offset))

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
            self.offset = None

    def set_user_info(self, nombre_completo, puesto, genero, login, password, cv_user):
        saludo = "Bienvenido(a)"
        if genero.lower() == 'masculino':
            saludo = "Bienvenido"
        elif genero.lower() == 'femenino':
            saludo = "Bienvenida"

        texto_bienvenida = f"{saludo}:\n{nombre_completo}\n({puesto})"
        self.ui.lbl_bienvenida.setText(texto_bienvenida)

        self.current_login = login
        self.current_password = password
        self.current_puesto = puesto
        self.current_cv_user = cv_user
        self.current_nombre_completo = nombre_completo

        self.ui.stackedWidget.setCurrentWidget(self.ui.Inicio)

    def cerrar_sesion(self):
        self.ui.lbl_bienvenida.setText("Bienvenido(a):")
        self.sesion_cerrada.emit()

    # --- MÓDULO: CAMBIAR PASSWORD ---

    def toggle_password_visibility(self, line_edit_widget):
        if line_edit_widget.echoMode() == QLineEdit.EchoMode.Password:
            line_edit_widget.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            line_edit_widget.setEchoMode(QLineEdit.EchoMode.Password)

    def validar_password_nuevo(self):
        """
        Valida los criterios del PDF en tiempo real y colorea las etiquetas.
        """
        password = self.ui.txt_pass_nuevo.text()
        all_criteria_valid = True

        try:
            # 1. Longitud
            if 4 <= len(password) <= 10:
                self.ui.caracter.setStyleSheet(self.style_crit_ok)
            else:
                self.ui.caracter.setStyleSheet(self.style_crit_error)
                all_criteria_valid = False

            # 2. Mayúscula
            if re.search(r"[A-Z]", password):
                self.ui.mayus.setStyleSheet(self.style_crit_ok)
            else:
                self.ui.mayus.setStyleSheet(self.style_crit_error)
                all_criteria_valid = False

            # 3. Minúscula
            if re.search(r"[a-z]", password):
                self.ui.minus.setStyleSheet(self.style_crit_ok)
            else:
                self.ui.minus.setStyleSheet(self.style_crit_error)
                all_criteria_valid = False

            # 4. Número
            if re.search(r"[0-9]", password):
                self.ui.numer.setStyleSheet(self.style_crit_ok)
            else:
                self.ui.numer.setStyleSheet(self.style_crit_error)
                all_criteria_valid = False

            # 5. Especial
            if re.search(r"[^a-zA-Z0-9]", password):
                self.ui.caracter_especial.setStyleSheet(self.style_crit_ok)
            else:
                self.ui.caracter_especial.setStyleSheet(self.style_crit_error)
                all_criteria_valid = False

            # Si el campo está vacío, resetear todo (no mostrar errores)
            if not password:
                self.limpiar_estilos_password(reset_field_color=False)
                all_criteria_valid = False

                # Colorear el QLineEdit en base a si TODO es válido
            if all_criteria_valid:
                self.ui.txt_pass_nuevo.setStyleSheet(self.style_qline_ok)
            else:
                # No lo ponemos en rojo si está vacío
                self.ui.txt_pass_nuevo.setStyleSheet(self.style_qline_error if password else self.style_qline_ok)

            # Validar el campo de repetir
            self.validar_password_repetido()

            return all_criteria_valid

        except AttributeError as e:
            print(f"Error al validar criterios (Faltan QLabels?): {e}")
            return False

    def validar_password_repetido(self):
        """
        Compara si 'Repetir Password' es igual a 'Password Nuevo'.
        """
        pass_nuevo = self.ui.txt_pass_nuevo.text()
        pass_repetir = self.ui.txt_pass_repetir.text()

        try:
            if not pass_repetir and not pass_nuevo:
                self.ui.txt_pass_repetir.setStyleSheet(self.style_qline_ok)
                return True

            if pass_nuevo == pass_repetir:
                self.ui.txt_pass_repetir.setStyleSheet(self.style_qline_ok)
                return True
            else:
                self.ui.txt_pass_repetir.setStyleSheet(self.style_qline_error)
                return False
        except AttributeError:
            return False  # El widget no existe

    def procesar_cambio_password(self):
        password_anterior = self.ui.txt_pass_anterior.text()
        password_nuevo = self.ui.txt_pass_nuevo.text()
        password_repetir = self.ui.txt_pass_repetir.text()

        login_actual = self.current_login
        password_actual_guardado = self.current_password

        # 1. Validar que la contraseña anterior sea correcta
        if not password_actual_guardado == password_anterior:
            QMessageBox.warning(self, "Acción denegada", "La contraseña anterior no es igual a la ingresada.")
            return

            # 2. Validar que los campos no estén vacíos
        if not password_nuevo or not password_repetir:
            QMessageBox.warning(self, "Error", "El campo 'Password Nuevo' y 'Repetir' no pueden estar vacíos.")
            return

        # 3. Validar que las nuevas contraseñas coincidan
        if password_nuevo != password_repetir:
            QMessageBox.warning(self, "Error", "Las nuevas contraseñas no coinciden.")
            return

        # 4. Validar que la nueva no sea igual a la anterior
        if password_nuevo == password_actual_guardado:
            QMessageBox.warning(self, "Error", "La nueva contraseña no puede ser igual a la anterior.")
            return

        # 5. Validar criterios del PDF (usamos la misma función de validación en vivo)
        if not (4 <= len(password_nuevo) <= 10) or \
                not re.search(r"[A-Z]", password_nuevo) or \
                not re.search(r"[a-z]", password_nuevo) or \
                not re.search(r"[0-9]", password_nuevo) or \
                not re.search(r"[^a-zA-Z0-9]", password_nuevo):  # <-- CAMBIO AQUÍ

            # Mensaje de error actualizado
            QMessageBox.warning(self, "Error",
                                "La contraseña nueva no cumple con todos los criterios (4-10 caracteres, 1 mayús, 1 min, 1 núm, 1 especial).")
            return

        # 6. Validar que la nueva contraseña no exista en la BD
        if self.db_manager.verificar_password_existente(password_nuevo):
            QMessageBox.warning(self, "Error", "Esa contraseña ya está en uso por otro usuario. Elija una diferente.")
            return

        # 7. Si todo es correcto, actualizar la BD
        exito = self.db_manager.actualizar_password(login_actual, password_nuevo)

        if exito:
            QMessageBox.information(self, "Éxito", "¡Contraseña actualizada correctamente!")
            self.current_password = password_nuevo  # Actualizamos la contraseña en memoria
            self.limpiar_campos_password()
        else:
            QMessageBox.critical(self, "Error de Base de Datos", "No se pudo actualizar la contraseña.")

    def limpiar_campos_password(self):
        try:
            self.ui.txt_pass_anterior.clear()
            self.ui.txt_pass_nuevo.clear()
            self.ui.txt_pass_repetir.clear()
            self.limpiar_estilos_password()
        except AttributeError:
            pass

    def limpiar_estilos_password(self, reset_field_color=True):
        """ Resetea todos los estilos de la página CambiarPass al estado 'OK' """
        try:
            if reset_field_color:
                self.ui.txt_pass_anterior.setStyleSheet(self.style_qline_ok)
                self.ui.txt_pass_nuevo.setStyleSheet(self.style_qline_ok)
                self.ui.txt_pass_repetir.setStyleSheet(self.style_qline_ok)

            # Siempre reseteamos las etiquetas de criterios (a rojo, como en la imagen)
            self.ui.caracter.setStyleSheet(self.style_crit_error)
            self.ui.mayus.setStyleSheet(self.style_crit_error)
            self.ui.minus.setStyleSheet(self.style_crit_error)
            self.ui.numer.setStyleSheet(self.style_crit_error)
            self.ui.caracter_especial.setStyleSheet(self.style_crit_error)
        except AttributeError:
            pass

    def configurar_botones_pagos(self, estado):
        """
        Implementa las reglas del profesor para habilitar/deshabilitar
        y cambiar el texto de los botones.
        """
        self.estado_actual_pagos = estado

        # Por defecto, obtenemos la fila seleccionada
        fila_seleccionada = self.ui.tabla_pagos.currentRow()

        if estado == "consultando":
            self.ui.btn_pagos_nuevo.setText("Nuevo")
            self.ui.btn_pagos_nuevo.setEnabled(True)

            self.ui.btn_pagos_actualizar.setText("Actualizar")
            self.ui.btn_pagos_actualizar.setEnabled(fila_seleccionada != -1)  # Activo solo si algo está seleccionado

            self.ui.btn_pagos_borrar.setText("Borrar")
            self.ui.btn_pagos_borrar.setEnabled(fila_seleccionada != -1)  # Activo solo si algo está seleccionado

            self.ui.btn_pagos_cancelar.setEnabled(False)
            self.ui.btn_pagos_consultar.setEnabled(False)

        elif estado == "nuevo":
            self.ui.btn_pagos_nuevo.setText("Guardar")
            self.ui.btn_pagos_nuevo.setEnabled(True)

            self.ui.btn_pagos_actualizar.setEnabled(False)
            self.ui.btn_pagos_borrar.setEnabled(False)
            self.ui.btn_pagos_cancelar.setEnabled(True)
            self.ui.btn_pagos_consultar.setEnabled(True)

        elif estado == "actualizando":
            self.ui.btn_pagos_nuevo.setEnabled(False)

            self.ui.btn_pagos_actualizar.setText("Guardar")
            self.ui.btn_pagos_actualizar.setEnabled(True)

            self.ui.btn_pagos_borrar.setEnabled(False)
            self.ui.btn_pagos_cancelar.setEnabled(True)
            self.ui.btn_pagos_consultar.setEnabled(True)

    def cargar_tabla_pagos(self):
        """Llena la tabla de pagos basándose en los permisos del usuario."""
        if self.current_puesto == 'Estudiante':
            datos_pagos = self.db_manager.get_pagos_por_usuario(self.current_cv_user)
            headers = ["ID Cobro", "Fecha", "Tipo", "Monto", "Descuento", "Estado", "Alumno"]
        else:
            datos_pagos = self.db_manager.get_todos_los_pagos()
            headers = ["ID Cobro", "Fecha", "Tipo", "Monto", "Descuento", "Estado", "Alumno", "ID Usuario"]

        self.ui.tabla_pagos.setColumnCount(len(headers))
        self.ui.tabla_pagos.setHorizontalHeaderLabels(headers)
        self.ui.tabla_pagos.setRowCount(len(datos_pagos))

        for row_idx, row_data in enumerate(datos_pagos):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.ui.tabla_pagos.setItem(row_idx, col_idx, item)

        header = self.ui.tabla_pagos.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ui.tabla_pagos.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ui.tabla_pagos.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.tabla_pagos.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Conectar la selección de la tabla para habilitar botones
        self.ui.tabla_pagos.itemSelectionChanged.connect(
            lambda: self.configurar_botones_pagos("consultando") if self.estado_actual_pagos == "consultando" else None
        )

    def cargar_combobox_alumnos(self):
        """Llena el ComboBox de alumnos en el formulario de pagos."""
        self.ui.combo_pagos_alumno.clear()

        if self.current_puesto == 'Estudiante':
            self.ui.combo_pagos_alumno.addItem(self.current_nombre_completo, self.current_cv_user)
            self.ui.combo_pagos_alumno.setEnabled(False)
        else:
            self.ui.combo_pagos_alumno.setEnabled(True)
            alumnos = self.db_manager.get_alumnos_para_combobox()
            self.ui.combo_pagos_alumno.addItem("Seleccione un alumno...", None)
            for cv_user, nombre_completo in alumnos:
                self.ui.combo_pagos_alumno.addItem(nombre_completo, cv_user)

    def cargar_combobox_pagos_y_descuentos(self):
        """Llena los ComboBox de Tipos de Pago y Descuentos."""

        # Cargar Tipos de Pago
        self.ui.combo_pagos_tipo.clear()
        tipos_pago = self.db_manager.get_tipos_pago()
        self.ui.combo_pagos_tipo.addItem("Seleccione un tipo...", (None, 0.0))  # (ID, Monto)
        for cv, ds, monto in tipos_pago:
            self.ui.combo_pagos_tipo.addItem(f"{ds} (${monto})", (cv, monto))

        # Cargar Descuentos
        self.ui.combo_pagos_descuento.clear()
        descuentos = self.db_manager.get_descuentos()
        self.ui.combo_pagos_descuento.addItem("Seleccione descuento...", (None, 0.0))  # (ID, Porcentaje)
        for cv, ds, porcentaje in descuentos:
            self.ui.combo_pagos_descuento.addItem(f"{ds} ({porcentaje * 100}%)", (cv, porcentaje))

        # Si el usuario es Estudiante, deshabilitar
        if self.current_puesto == 'Estudiante':
            self.ui.combo_pagos_tipo.setEnabled(False)
            self.ui.combo_pagos_descuento.setEnabled(False)
        else:
            self.ui.combo_pagos_tipo.setEnabled(True)
            self.ui.combo_pagos_descuento.setEnabled(True)

    def actualizar_monto_y_total(self):
        """Se llama cada vez que cambia un QComboBox. Calcula el total."""

        # 1. Obtener datos de los ComboBox
        # currentData() devuelve la tupla (ID, Valor) que guardamos
        tipo_data = self.ui.combo_pagos_tipo.currentData()
        desc_data = self.ui.combo_pagos_descuento.currentData()

        monto = 0.0
        porcentaje_desc = 0.0

        if tipo_data and tipo_data[0] is not None:
            monto = float(tipo_data[1])

        if desc_data and desc_data[0] is not None:
            porcentaje_desc = float(desc_data[1])

        # 2. Calcular valores
        monto_descuento = monto * porcentaje_desc
        total = monto - monto_descuento

        # 3. Mostrar valores en los QLineEdit (formateados como dinero)
        locale = QLocale(QLocale.Language.Spanish, QLocale.Country.Mexico)
        self.ui.txt_pagos_monto.setText(locale.toString(monto, 'f', 2))
        self.ui.txt_pagos_total.setText(locale.toString(total, 'f', 2))

    def limpiar_formulario_pagos(self):
        """Limpia todos los campos del formulario de pagos."""
        self.ui.lbl_pagos_user_dinamico.setText(self.current_nombre_completo)
        self.ui.date_pagos_fecha.setDate(QDate.currentDate())
        self.ui.combo_pagos_tipo.setCurrentIndex(0)
        self.ui.combo_pagos_descuento.setCurrentIndex(0)
        self.ui.txt_pagos_monto.clear()
        self.ui.txt_pagos_total.clear()
        self.ui.combo_pagos_estado.setCurrentIndex(0)
        if self.current_puesto != 'Estudiante':
            self.ui.combo_pagos_alumno.setCurrentIndex(0)
        self.current_pago_id_edicion = None

    def accion_pagos_nuevo(self):
        if self.estado_actual_pagos == "nuevo":
            self.guardar_nuevo_pago()
        else:
            self.ui.stackedWidget_pagos.setCurrentWidget(self.ui.pagos_page_formulario)
            self.limpiar_formulario_pagos()
            self.configurar_botones_pagos("nuevo")

    def accion_pagos_actualizar(self):
        if self.estado_actual_pagos == "actualizando":
            self.guardar_actualizacion_pago()
        else:
            QMessageBox.information(self, "Pendiente",
                                    "La lógica de 'Actualizar' (cargar datos) aún no está implementada.")
            # self.ui.stackedWidget_pagos.setCurrentWidget(self.ui.pagos_page_formulario)
            # self.configurar_botones_pagos("actualizando")

    def accion_pagos_borrar(self):
        QMessageBox.information(self, "Pendiente", "La lógica de 'Borrar' aún no está implementada.")

    def accion_pagos_consultar(self):
        """Vuelve a la vista de tabla (consulta)."""
        self.ui.stackedWidget_pagos.setCurrentWidget(self.ui.pagos_page_consulta)
        self.configurar_botones_pagos("consultando")
        self.cargar_tabla_pagos()

    def accion_pagos_cancelar(self):
        """Cancela la acción de 'Nuevo' o 'Actualizar' y vuelve a la consulta."""
        self.accion_pagos_consultar()

    def accion_pagos_regresar(self):
        """Regresa al menú de inicio del stackedWidget principal."""
        self.ui.stackedWidget.setCurrentWidget(self.ui.Inicio)
        if self.menu_esta_oculto:
            self.toggle_menu_main()

    def guardar_nuevo_pago(self):
        """Valida los datos del formulario y llama al db_manager para INSERTAR."""
        # 1. Obtener datos del formulario
        cv_usuario = self.ui.combo_pagos_alumno.currentData()
        fecha = self.ui.date_pagos_fecha.date().toString("yyyy-MM-dd")

        tipo_data = self.ui.combo_pagos_tipo.currentData()
        desc_data = self.ui.combo_pagos_descuento.currentData()

        estado = self.ui.combo_pagos_estado.currentText()

        # 2. Validar datos
        if not cv_usuario:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un alumno.")
            return
        if not tipo_data or tipo_data[0] is None:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un Tipo de Pago.")
            return
        if not desc_data or desc_data[0] is None:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un Descuento.")
            return

        # 3. Obtener valores finales para la BD
        # El 'Tipo' que guardamos es el string (ej. "Mensualidad")
        # El 'Monto' y 'Descuento' son los valores numéricos calculados

        tipo_str = self.ui.combo_pagos_tipo.currentText().split(" (")[0]  # Obtiene "Mensualidad"
        monto_final = float(tipo_data[1])
        porcentaje_final = float(desc_data[1])
        descuento_calculado = monto_final * porcentaje_final  # Guardamos el monto del descuento

        # 4. Enviar a la Base de Datos
        exito = self.db_manager.add_pago(
            cv_usuario=cv_usuario,
            fecha=fecha,
            tipo=tipo_str,
            monto=monto_final,
            descuento=descuento_calculado,
            estado=estado
        )

        # 5. Informar al usuario y recargar
        if exito:
            QMessageBox.information(self, "Éxito", "Pago registrado correctamente.")
            self.accion_pagos_consultar()  # Volver a la tabla
        else:
            QMessageBox.critical(self, "Error de BD", "No se pudo registrar el pago en la base de datos.")
