import re
from PyQt6.QtCore import (
    Qt, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup
)
from PyQt6.QtGui import QMouseEvent, QIcon, QDoubleValidator
from PyQt6.QtWidgets import QDialog, QHeaderView, QLineEdit, QMessageBox, QTableWidgetItem, QAbstractItemView, QCompleter
from PyQt6.QtCore import QDate, QLocale, Qt
from datetime import date
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
            ruta_icono = "Gui\\../../Imagenes/eye_on_see_show_view_vision_watch_icon_123215.png"
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
        self.estado_actual_personas = "consultando"
        self.estado_actual_catalogos = "consultando"
        self.estado_actual_asistencia = "consultando"
        self.estado_actual_evaluaciones = "consultando"

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
        self.ui.btn_Personas.clicked.connect(self.mostrar_pagina_personas)
        self.ui.btn_catalogos.clicked.connect(self.mostrar_pagina_catalogos)
        self.ui.btn_asistencia.clicked.connect(self.mostrar_pagina_asistencia)
        self.ui.btn_evaluaciones.clicked.connect(self.mostrar_pagina_evaluaciones)

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
            self.ui.filtro_pagos_nombre.textChanged.connect(self.actualizar_filtros_tabla)
            self.ui.filtro_pagos_estado.currentIndexChanged.connect(self.actualizar_filtros_tabla)

            # Conectar señales de los ComboBox
            self.ui.combo_pagos_tipo.currentIndexChanged.connect(self.actualizar_monto_y_total)
            self.ui.combo_pagos_descuento.currentIndexChanged.connect(self.actualizar_monto_y_total)
            self.ui.combo_pagos_estado.addItems(["Pagado", "Pendiente"])

            # Poner validadores a los campos de dinero (para que muestren $0.00)
            locale = QLocale(QLocale.Language.Spanish, QLocale.Country.Mexico)
            validator = QDoubleValidator(0.0, 99999.99, 2)
            validator.setLocale(locale)
            validator.setNotation(QDoubleValidator.Notation.StandardNotation)

            self.ui.txt_pagos_monto.setValidator(validator)
            self.ui.txt_pagos_total.setValidator(validator)

        except AttributeError as e:
            print(f"ADVERTENCIA: No se pudieron conectar los widgets de Pagos. ¿Regeneraste el UI? Error: {e}")

        try:
            # Botones de acción
            self.ui.btn_per_nuevo.clicked.connect(self.accion_personas_nuevo)
            self.ui.btn_per_actualizar.clicked.connect(self.accion_personas_actualizar)  # <-- CONECTADO
            self.ui.btn_per_borrar.clicked.connect(self.accion_personas_borrar) # <-- (Aún pendiente)
            self.ui.btn_per_consultar.clicked.connect(self.accion_personas_consultar)
            self.ui.btn_per_cancelar.clicked.connect(self.accion_personas_cancelar)
            self.ui.btn_per_regresar.clicked.connect(self.accion_personas_regresar)

            # Filtros de la tabla
            self.ui.filtro_personas_nombre.textChanged.connect(self.actualizar_filtros_tabla_personas)
            self.ui.filtro_personas_tipo.currentIndexChanged.connect(self.actualizar_filtros_tabla_personas)

            # --- AÑADE ESTA CONEXIÓN ---
            # Conectar la selección de la tabla para habilitar/deshabilitar botones
            self.ui.tabla_personas.itemSelectionChanged.connect(
                lambda: self.configurar_botones_personas(
                    "consultando") if self.estado_actual_personas == "consultando" else None
            )
            # --- FIN DE LA CONEXIÓN ---

            # Llenar ComboBox de estado (el único estático)
            self.ui.combo_per_edocta.addItems(["True", "False"])

        except AttributeError as e:
            print(f"ADVERTENCIA: No se pudieron conectar los widgets de Personas. ¿Regeneraste el UI? Error: {e}")
            # --- CONEXIONES MÓDULO CATÁLOGOS (Lógica de botones) ---
        try:
            self.ui.btn_cata_nuevo.clicked.connect(self.accion_catalogos_nuevo)
            self.ui.btn_cata_actualizar.clicked.connect(self.accion_catalogos_actualizar)
            self.ui.btn_cata_borrar.clicked.connect(self.accion_catalogos_borrar)
            self.ui.btn_cata_consultar.clicked.connect(self.accion_catalogos_consultar)
            # Cancelar y Consultar/Regresar hacen lo mismo (volver al estado "consultando")
            self.ui.btn_cata_cancelar.clicked.connect(self.accion_catalogos_consultar)
            # Reutilizamos la función de regresar de los otros módulos
            self.ui.btn_cata_regresar.clicked.connect(self.accion_pagos_regresar)
        except AttributeError as e:
            print(f"ADVERTENCIA: No se pudieron conectar los widgets de Catálogos. {e}")

        # --- CONEXIONES MÓDULO ASISTENCIA (Lógica de botones) ---
        try:
            self.ui.btn_asis_nuevo.clicked.connect(self.accion_asistencia_nuevo)
            self.ui.btn_asis_actualizar.clicked.connect(self.accion_asistencia_actualizar)
            self.ui.btn_asis_borrar.clicked.connect(self.accion_asistencia_borrar)
            self.ui.btn_asis_consultar.clicked.connect(self.accion_asistencia_consultar)
            self.ui.btn_asis_cancelar.clicked.connect(self.accion_asistencia_consultar)
            self.ui.btn_asis_regresar.clicked.connect(self.accion_pagos_regresar)
        except AttributeError as e:
            print(f"ADVERTENCIA: No se pudieron conectar los widgets de Asistencia. {e}")

        # --- CONEXIONES MÓDULO EVALUACIONES (Lógica de botones) ---
        try:
            self.ui.btn_eva_nuevo.clicked.connect(self.accion_evaluaciones_nuevo)
            self.ui.btn_eva_actualizar.clicked.connect(self.accion_evaluaciones_actualizar)
            self.ui.btn_eva_borrar.clicked.connect(self.accion_evaluaciones_borrar)
            self.ui.btn_eva_consultar.clicked.connect(self.accion_evaluaciones_consultar)
            self.ui.btn_eva_cancelar.clicked.connect(self.accion_evaluaciones_consultar)
            self.ui.btn_eva_regresar.clicked.connect(self.accion_pagos_regresar)
        except AttributeError as e:
            print(f"ADVERTENCIA: No se pudieron conectar los widgets de Evaluaciones. {e}")


    # --- MÓDULO: NAVEGACIÓN DE PÁGINAS ---
    def mostrar_pagina_pagos(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.Pagos)

            self.db_manager.registrar_acceso(
                self.current_login, True, "AUDITORIA APP: Acceso al módulo de Pagos"
            )

            self.cargar_tabla_pagos()

            self.cargar_combobox_alumnos()

            self.cargar_combobox_pagos_y_descuentos()

            self.cargar_combobox_filtro_estado()

            if not self.menu_esta_oculto:
                self.toggle_menu_main()

            self.accion_pagos_consultar()
        except AttributeError as e:
            print(e)

    def mostrar_pagina_cambiarpass(self):
        try:
            # Asumiendo que se llama 'page_7'
            self.ui.stackedWidget.setCurrentWidget(self.ui.Cambiarpass)

            self.db_manager.registrar_acceso(
                self.current_login, True, "AUDITORIA APP: Acceso al módulo CambiarPass"
            )

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

    def mostrar_pagina_catalogos(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.Catalogos)
            self.db_manager.registrar_acceso(
                self.current_login, True, "AUDITORIA APP: Acceso al modulo de Catalogos"
            )
            # --- AÑADIDO: Configurar estado inicial ---
            self.accion_catalogos_consultar()
            if not self.menu_esta_oculto:
                self.toggle_menu_main()
            # --- FIN DE AÑADIDO ---
        except AttributeError as e:
            print(f"Error: La pagina(Catalogos) no existe. creela en Qt Designer. {e}")

    def mostrar_pagina_asistencia(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.Asistencia)
            self.db_manager.registrar_acceso(
                self.current_login, True, "Auditoria APP: Acceso al modulo de Asistencia"
            )
            # --- AÑADIDO: Configurar estado inicial ---
            self.accion_asistencia_consultar()
            if not self.menu_esta_oculto:
                self.toggle_menu_main()
            # --- FIN DE AÑADIDO ---
        except AttributeError as e:
            print(f"Error: La pagina (asistencias) no existe. creela en Qt Designer. {e}")

    def mostrar_pagina_evaluaciones(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.Evaluaciones)
            self.db_manager.registrar_acceso(
                self.current_login, True, "Auditoria APP: Acceso al modulo de Evaluaciones"
            )
            # --- AÑADIDO: Configurar estado inicial ---
            self.accion_evaluaciones_consultar()
            if not self.menu_esta_oculto:
                self.toggle_menu_main()
            # --- FIN DE AÑADIDO ---
        except AttributeError as e:
            print(f"Erro: La pagina (evaluaciones) no existe. creela en Qt Designer. {e}")

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
            self.ui.btn_pagos_consultar.setEnabled(True)

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
        """Llena el ComboBox de alumnos con filtro y auto-completado
        para el director, o lo bloqueara para el estudiante."""
        self.ui.combo_pagos_alumno.clear()

        if self.current_puesto == 'Estudiante':
            self.ui.combo_pagos_alumno.addItem(self.current_nombre_completo, self.current_cv_user)
            self.ui.combo_pagos_alumno.setEnabled(False)
            self.ui.combo_pagos_alumno.setEditable(False)
        else:
            self.ui.combo_pagos_alumno.setEnabled(True)
            self.ui.combo_pagos_alumno.setEditable(True)
            alumnos = self.db_manager.get_alumnos_para_combobox()
            nombres_alumnos = []
            self.ui.combo_pagos_alumno.addItem("Seleccionar alumno...", None)
            for cv_user, nombre_completo in alumnos:
                self.ui.combo_pagos_alumno.addItem(nombre_completo, cv_user)
                nombres_alumnos.append(nombre_completo)

            completer = QCompleter(nombres_alumnos)

            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)

            self.ui.combo_pagos_alumno.setCompleter(completer)

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

    def accion_pagos_nuevo(self):
        if self.estado_actual_pagos == "nuevo":
            self.guardar_nuevo_pago()
        else:
            self.ui.stackedWidget_pagos.setCurrentWidget(self.ui.pagos_page_formulario)
            self.limpiar_formulario_pagos()
            self.current_pago_id_edicion = None
            self.configurar_botones_pagos("nuevo")

    def accion_pagos_actualizar(self):
        if self.estado_actual_pagos == "actualizando":
            # Si el estado es "actualizando", el botón dice "Guardar".
            self.guardar_actualizacion_pago()
        else:
            # Si el estado es "consultando", el botón dice "Actualizar".
            # 1. Obtener la fila seleccionada
            fila = self.ui.tabla_pagos.currentRow()
            if fila == -1:
                QMessageBox.warning(self, "Error", "No has seleccionado ningún pago para actualizar.")
                return

            # 2. Determinar las columnas (pueden cambiar si es admin o estudiante)
            headers = [self.ui.tabla_pagos.horizontalHeaderItem(c).text() for c in
                       range(self.ui.tabla_pagos.columnCount())]

            # 3. Leer los datos de la tabla
            try:
                # Usamos un diccionario para que sea más fácil de leer
                datos_fila = {}
                for idx, header in enumerate(headers):
                    datos_fila[header] = self.ui.tabla_pagos.item(fila, idx).text()

                # 4. Guardar el ID del pago que estamos editando
                self.current_pago_id_edicion = int(datos_fila["ID Cobro"])

                # 5. Cargar los datos en el formulario
                self.limpiar_formulario_pagos()  # Limpia y resetea

                # Usamos nuestro "ayudante" para seleccionar los ComboBox
                self._set_combo_by_text(self.ui.combo_pagos_alumno, datos_fila["Alumno"])
                self._set_combo_by_text(self.ui.combo_pagos_tipo, datos_fila["Tipo"])

                # Para el descuento, calculamos el porcentaje
                monto = float(datos_fila["Monto"])
                descuento = float(datos_fila["Descuento"])
                if monto > 0:
                    porcentaje_buscado = (descuento / monto) * 100
                    self._set_combo_by_text(self.ui.combo_pagos_descuento, f"({porcentaje_buscado:.2f}%)")
                else:
                    self.ui.combo_pagos_descuento.setCurrentIndex(0)  # Sin descuento

                self.ui.combo_pagos_estado.setCurrentText(datos_fila["Estado"])

                # Cargar la fecha
                fecha = QDate.fromString(datos_fila["Fecha"], "yyyy-MM-dd")
                self.ui.date_pagos_fecha.setDate(fecha)

                # 6. Cambiar de vista y de estado
                self.ui.stackedWidget_pagos.setCurrentWidget(self.ui.pagos_page_formulario)
                self.configurar_botones_pagos("actualizando")

            except Exception as e:
                print(f"Error al leer los datos de la tabla: {e}")
                QMessageBox.critical(self, "Error", "No se pudieron cargar los datos de la fila seleccionada.")

    def accion_pagos_borrar(self):
        """
        Toma la fila seleccionada, pide confirmación y la elimina.
        """
        # 1. Obtener la fila seleccionada
        fila = self.ui.tabla_pagos.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "No has seleccionado ningún pago para borrar.")
            return

        try:
            # 2. Obtener el ID Cobro (siempre es la columna 0)
            id_cobro_item = self.ui.tabla_pagos.item(fila, 0)
            id_a_borrar = int(id_cobro_item.text())

            # 3. Obtener el nombre del Alumno para un mensaje más claro
            col_alumno_idx = -1
            for col in range(self.ui.tabla_pagos.columnCount()):
                header = self.ui.tabla_pagos.horizontalHeaderItem(col).text()
                if header == "Alumno":
                    col_alumno_idx = col
                    break

            nombre_alumno = self.ui.tabla_pagos.item(fila,
                                                     col_alumno_idx).text() if col_alumno_idx != -1 else "el pago seleccionado"

            # 4. Pedir confirmación al usuario (Regla de seguridad)
            confirmacion = QMessageBox.question(self, "Confirmar Eliminación",
                                                f"¿Estás seguro de que deseas eliminar el pago de {nombre_alumno} (ID: {id_a_borrar})?\n\nEsta acción no se puede deshacer.",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            # 5. Si el usuario confirma
            if confirmacion == QMessageBox.StandardButton.Yes:
                # 6. Llamar a la BD para eliminar
                exito = self.db_manager.delete_pago(id_a_borrar, self.current_login)

                if exito:
                    QMessageBox.information(self, "Éxito", "El pago ha sido eliminado correctamente.")
                    self.cargar_tabla_pagos()  # Recargar la tabla
                else:
                    QMessageBox.critical(self, "Error de BD", "No se pudo eliminar el pago.")

        except Exception as e:
            print(f"Error al borrar pago: {e}")
            QMessageBox.critical(self, "Error", "No se pudo obtener el ID del pago a borrar.")

    def accion_pagos_consultar(self):
        """Vuelve a la vista de tabla (consulta), RECARTGA los datos
        y LIMPIA los filtros."""
        self.ui.stackedWidget_pagos.setCurrentWidget(self.ui.pagos_page_consulta)
        self.configurar_botones_pagos("consultando")

        self.ui.filtro_pagos_nombre.clear()
        self.ui.filtro_pagos_estado.setCurrentIndex(0)
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

        # --- INICIO DE LÓGICA DE VALIDACIÓN DE ALUMNO CORREGIDA ---

        # 1. Obtener el texto actual del ComboBox
        texto_alumno = self.ui.combo_pagos_alumno.currentText()
        cv_usuario = None  # Reiniciamos el ID

        # 2. Revisar que no sea el texto por defecto
        if texto_alumno != "Seleccione un alumno...":
            # 3. Buscar el texto en la lista del ComboBox
            # Usamos MatchExactly para asegurarnos de que el texto es idéntico a uno de la lista
            index = self.ui.combo_pagos_alumno.findText(texto_alumno, Qt.MatchFlag.MatchExactly)

            if index != -1:  # Si SÍ lo encontró en la lista
                # 4. Obtenemos el ID (cv_user) guardado en ese índice
                cv_usuario = self.ui.combo_pagos_alumno.itemData(index)

        # --- FIN DE LÓGICA CORREGIDA ---

        # 5. Obtener el resto de los datos (esto ya estaba bien)
        fecha = self.ui.date_pagos_fecha.date().toString("yyyy-MM-dd")
        tipo_data = self.ui.combo_pagos_tipo.currentData()
        desc_data = self.ui.combo_pagos_descuento.currentData()
        estado = self.ui.combo_pagos_estado.currentText()

        # 6. Validar datos
        if not cv_usuario:
            # Esta validación ahora es más inteligente:
            if texto_alumno == "Seleccione un alumno...":
                QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un alumno.")
            else:
                # Este es el nuevo caso: el usuario escribió un nombre que NO existe
                QMessageBox.warning(self, "Alumno no encontrado",
                                    f"El alumno '{texto_alumno}' no existe.\n\n"
                                    "Por favor, créelo primero en el módulo 'Personas' "
                                    "antes de registrarle un pago.")
            return

        if not tipo_data or tipo_data[0] is None:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un Tipo de Pago.")
            return
        if not desc_data or desc_data[0] is None:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un Descuento.")
            return

        # 7. Obtener valores finales para la BD (esto ya estaba bien)
        tipo_str = self.ui.combo_pagos_tipo.currentText().split(" (")[0]
        monto_final = float(tipo_data[1])
        porcentaje_final = float(desc_data[1])
        descuento_calculado = monto_final * porcentaje_final

        # 8. Enviar a la Base de Datos (esto ya estaba bien)
        exito = self.db_manager.add_pago(
            cv_usuario=cv_usuario,
            fecha=fecha,
            tipo=tipo_str,
            monto=monto_final,
            descuento=descuento_calculado,
            estado=estado,
            admin_login=self.current_login
        )

        # 9. Informar al usuario y recargar (esto ya estaba bien)
        if exito:
            QMessageBox.information(self, "Éxito", "Pago registrado correctamente.")
            self.accion_pagos_consultar()  # Volver a la tabla
        else:
            QMessageBox.critical(self, "Error de BD", "No se pudo registrar el pago en la base de datos.")


    def cargar_combobox_filtro_estado(self):
        """Llena el combobox de filtro con los estados de pago."""
        self.ui.filtro_pagos_estado.clear()
        self.ui.filtro_pagos_estado.addItem("Todos")
        self.ui.filtro_pagos_estado.addItem("Pagado")
        self.ui.filtro_pagos_estado.addItem("Pendiente")

    def actualizar_filtros_tabla(self):
        """Filtra la tabla en vivo basado en el QlineEdit de nombre
        y el QcomboBox de estado.
        """
        #1. Obtener los valores de los filtros
        filtro_nombre =  self.ui.filtro_pagos_nombre.text().lower()
        filtro_estado = self.ui.filtro_pagos_estado.currentText()

        #Determinar las columnas correctas
        col_alumno_idx = -1
        col_estado_idx = -1

        for col in range(self.ui.tabla_pagos.columnCount()):
            header = self.ui.tabla_pagos.horizontalHeaderItem(col).text()
            if header == "Alumno":
                col_alumno_idx = col
            elif header == "Estado":
                col_estado_idx = col

        if col_alumno_idx == -1 or col_estado_idx == -1:
            print("Error no se encontraron las columnas 'Alumno' o 'Estado para filtrar.'")

        #2. Iterar sobre todas las filas de la tabla
        for fila in range(self.ui.tabla_pagos.rowCount()):
            #3. Obtener el texto de las celdas de alumno y estado
            item_alumno = self.ui.tabla_pagos.item(fila, col_alumno_idx).text().lower()
            item_estado = self.ui.tabla_pagos.item(fila, col_estado_idx).text()

            #4. Comprobar si coinciden con los filtros
            match_nombre = filtro_nombre in item_alumno
            match_estado = (filtro_estado == "Todos" or filtro_estado == item_estado)

            #5. Ocultar o mostrar la fila
            if match_nombre and match_estado:
                self.ui.tabla_pagos.setRowHidden(fila, False)
            else:
                self.ui.tabla_pagos.setRowHidden(fila, True)

    def _set_combo_by_text(self, combobox, texto_a_buscar):
        """
        Busca un texto en un QComboBox y lo selecciona.
        Usa 'MatchContains' para encontrar (ej. "Inscripción" en "Inscripción ($500.00)")
        """
        if not texto_a_buscar:
            combobox.setCurrentIndex(0)  # Poner en "Seleccione..."
            return

        # findText devuelve el índice de la primera coincidencia
        index = combobox.findText(texto_a_buscar, Qt.MatchFlag.MatchContains)

        if index != -1:  # Si lo encontró
            combobox.setCurrentIndex(index)
        else:
            combobox.setCurrentIndex(0)  # No se encontró, poner en "Seleccione..."

    def guardar_actualizacion_pago(self):
        """Valida y guarda los datos de un pago MODIFICADO."""

        # 1. Obtener el ID del pago que estamos editando
        if self.current_pago_id_edicion is None:
            QMessageBox.critical(self, "Error", "No se ha seleccionado ningún pago para actualizar.")
            return

        cv_cobro = self.current_pago_id_edicion

        # 2. Obtener datos del formulario (es la misma lógica de "Nuevo")
        texto_alumno = self.ui.combo_pagos_alumno.currentText()
        cv_usuario = None
        if texto_alumno != "Seleccione un alumno...":
            index = self.ui.combo_pagos_alumno.findText(texto_alumno, Qt.MatchFlag.MatchExactly)
            if index != -1:
                cv_usuario = self.ui.combo_pagos_alumno.itemData(index)

        fecha = self.ui.date_pagos_fecha.date().toString("yyyy-MM-dd")
        tipo_data = self.ui.combo_pagos_tipo.currentData()
        desc_data = self.ui.combo_pagos_descuento.currentData()
        estado = self.ui.combo_pagos_estado.currentText()

        # 3. Validar datos
        if not cv_usuario:
            QMessageBox.warning(self, "Datos incompletos", "El alumno seleccionado no es válido.")
            return
        if not tipo_data or tipo_data[0] is None:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un Tipo de Pago.")
            return
        if not desc_data or desc_data[0] is None:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un Descuento.")
            return

        # 4. Obtener valores finales para la BD
        tipo_str = self.ui.combo_pagos_tipo.currentText().split(" (")[0]
        monto_final = float(tipo_data[1])
        porcentaje_final = float(desc_data[1])
        descuento_calculado = monto_final * porcentaje_final

        # 5. Enviar a la Base de Datos (¡Llamamos a UPDATE!)
        exito = self.db_manager.update_pago(
            cv_cobro=cv_cobro,
            cv_usuario=cv_usuario,
            fecha=fecha,
            tipo=tipo_str,
            monto=monto_final,
            descuento=descuento_calculado,
            estado=estado,
            admin_login=self.current_login
        )

        # 6. Informar al usuario y recargar
        if exito:
            QMessageBox.information(self, "Éxito", "Pago actualizado correctamente.")
            self.accion_pagos_consultar()  # Volver a la tabla
        else:
            QMessageBox.critical(self, "Error de BD", "No se pudo actualizar el pago.")

    # =================================================================
    # === MÓDULO: GESTIÓN DE PERSONAS (USUARIOS)
    # =================================================================

    def mostrar_pagina_personas(self):
        """
        Se llama al presionar el botón 'Personas' del menú principal.
        Prepara la página de gestión de personas.
        """
        try:
            # 1. Registrar auditoría de aplicación
            self.db_manager.registrar_acceso(
                self.current_login, True, "AUDITORIA APP: Acceso al módulo de Personas"
            )

            # 2. Cambiar a la página de personas
            self.ui.stackedWidget.setCurrentWidget(self.ui.Personas)

            # 3. Cargar los QComboBox del formulario (Género, Puesto, etc.)
            self.cargar_combobox_catalogos_personas()

            # 4. Cargar el QComboBox del filtro de la tabla
            self.cargar_combobox_filtro_tipo_persona()

            # 5. Ocultar el menú lateral
            if not self.menu_esta_oculto:
                self.toggle_menu_main()

            # 6. Poner en estado de consulta (mostrar tabla)
            self.accion_personas_consultar()

        except AttributeError as e:
            print(f"Error crítico al mostrar 'page_personas'. Revisa el nombre en Qt Designer. Error: {e}")

    def cargar_combobox_catalogos_personas(self):
        """
        Llena todos los QComboBox del formulario de Personas
        con datos de la base de datos.
        """
        # --- Llenar ComboBox de Género ---
        self.ui.combo_per_genero.clear()
        self.ui.combo_per_genero.addItem("Seleccione...", None)
        generos = self.db_manager.get_generos()
        for cv, ds in generos:
            self.ui.combo_per_genero.addItem(ds, cv)  # Guarda el ID (CvGenero)

        # --- Llenar ComboBox de Puesto ---
        self.ui.combo_per_puesto.clear()
        self.ui.combo_per_puesto.addItem("Seleccione...", None)
        puestos = self.db_manager.get_puestos()
        for cv, ds in puestos:
            self.ui.combo_per_puesto.addItem(ds, cv)  # Guarda el ID (CvPuesto)

        # --- Llenar ComboBox de Tipo de Persona ---
        self.ui.combo_per_tipopersona.clear()
        self.ui.combo_per_tipopersona.addItem("Seleccione...", None)
        tipos = self.db_manager.get_tipos_persona()
        for cv, ds in tipos:
            self.ui.combo_per_tipopersona.addItem(ds, cv)  # Guarda el ID (CvTpPerson)

    def cargar_combobox_filtro_tipo_persona(self):
        """Llena el ComboBox de filtro de la tabla de personas."""
        self.ui.filtro_personas_tipo.clear()
        self.ui.filtro_personas_tipo.addItem("Todos")
        # Obtenemos los datos frescos de la BD
        tipos = self.db_manager.get_tipos_persona()
        for cv, ds in tipos:
            self.ui.filtro_personas_tipo.addItem(ds)

    def cargar_tabla_personas(self):
        """Llena la tabla de consulta de personas."""
        datos_personas = self.db_manager.get_all_personas_info()

        # Definir los headers basados en la consulta
        headers = ["ID Usuario", "Login", "Nombre Completo", "Tipo", "Puesto", "E-mail", "Telefono", "EdoCta"]

        self.ui.tabla_personas.setColumnCount(len(headers))
        self.ui.tabla_personas.setHorizontalHeaderLabels(headers)
        self.ui.tabla_personas.setRowCount(len(datos_personas))

        for row_idx, row_data in enumerate(datos_personas):
            for col_idx, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))
                self.ui.tabla_personas.setItem(row_idx, col_idx, item)

        # Configurar la apariencia de la tabla
        header = self.ui.tabla_personas.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ui.tabla_personas.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.ui.tabla_personas.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.ui.tabla_personas.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Conectar la selección de la tabla para habilitar botones (si es necesario en el futuro)
        # self.ui.tabla_personas.itemSelectionChanged.connect(...)

    def limpiar_formulario_personas(self):
        """Limpia todos los campos del formulario de Personas."""
        self.ui.lbl_per_user_dinamico.setText(self.current_nombre_completo)  # Asegúrate que el label se llame así

        # Limpiar QLineEdit
        self.ui.txt_per_nombre.clear()
        self.ui.txt_per_apepat.clear()
        self.ui.txt_per_apemat.clear()
        self.ui.txt_per_email.clear()
        self.ui.txt_per_telefono.clear()
        self.ui.txt_per_login.clear()
        self.ui.txt_per_password.clear()

        # Resetear QDateEdit
        self.ui.date_per_fecnac.setDate(QDate(2000, 1, 1))
        self.ui.date_per_fecini.setDate(QDate.currentDate())
        self.ui.date_per_fecven.setDate(QDate.currentDate().addYears(1))

        # Resetear QComboBox
        self.ui.combo_per_genero.setCurrentIndex(0)
        self.ui.combo_per_puesto.setCurrentIndex(0)
        self.ui.combo_per_tipopersona.setCurrentIndex(0)
        self.ui.combo_per_edocta.setCurrentIndex(0)  # "True"

        # (Guardamos el ID del usuario que se está editando. None si es nuevo)
        self.current_persona_id_edicion = None

    def configurar_botones_personas(self, estado):
        """Gestiona los botones del módulo de Personas."""

        self.estado_actual_personas = estado  # <-- ¡Esta línea es crucial!
        fila_seleccionada = self.ui.tabla_personas.currentRow()

        if estado == "consultando":
            self.ui.btn_per_nuevo.setText("Nuevo")
            self.ui.btn_per_nuevo.setEnabled(True)
            self.ui.btn_per_actualizar.setText("Actualizar")
            self.ui.btn_per_actualizar.setEnabled(fila_seleccionada != -1)
            self.ui.btn_per_borrar.setText("Borrar")
            self.ui.btn_per_borrar.setEnabled(fila_seleccionada != -1)  # Habilitar/deshabilitar
            self.ui.btn_per_cancelar.setEnabled(False)
            self.ui.btn_per_consultar.setEnabled(True)

        elif estado == "nuevo":
            self.ui.btn_per_nuevo.setText("Guardar")  # "Nuevo" se convierte en "Guardar"
            self.ui.btn_per_nuevo.setEnabled(True)
            self.ui.btn_per_actualizar.setText("Actualizar")  # "Actualizar" se deshabilita
            self.ui.btn_per_actualizar.setEnabled(False)
            self.ui.btn_per_borrar.setEnabled(False)
            self.ui.btn_per_cancelar.setEnabled(True)
            self.ui.btn_per_consultar.setEnabled(True)

        elif estado == "actualizando":
            self.ui.btn_per_nuevo.setText("Nuevo")  # "Nuevo" se deshabilita
            self.ui.btn_per_nuevo.setEnabled(False)
            self.ui.btn_per_actualizar.setText("Guardar")  # "Actualizar" se convierte en "Guardar"
            self.ui.btn_per_actualizar.setEnabled(True)
            self.ui.btn_per_borrar.setEnabled(False)
            self.ui.btn_per_cancelar.setEnabled(True)
            self.ui.btn_per_consultar.setEnabled(True)

    def actualizar_filtros_tabla_personas(self):
        """Filtra la tabla de personas en vivo."""
        filtro_nombre = self.ui.filtro_personas_nombre.text().lower()
        filtro_tipo = self.ui.filtro_personas_tipo.currentText()

        # Columnas fijas de la consulta 'get_all_personas_info'
        col_nombre_idx = 2
        col_tipo_idx = 3

        for fila in range(self.ui.tabla_personas.rowCount()):
            item_nombre = self.ui.tabla_personas.item(fila, col_nombre_idx).text().lower()
            item_tipo = self.ui.tabla_personas.item(fila, col_tipo_idx).text()

            match_nombre = filtro_nombre in item_nombre
            match_tipo = (filtro_tipo == "Todos" or filtro_tipo == item_tipo)

            if match_nombre and match_tipo:
                self.ui.tabla_personas.setRowHidden(fila, False)
            else:
                self.ui.tabla_personas.setRowHidden(fila, True)

    # --- ACCIONES DE BOTONES (Personas) ---

    def accion_personas_nuevo(self):
        if self.estado_actual_personas == "nuevo":  # Debería ser estado_actual_personas
            self.guardar_nueva_persona()
        else:
            self.ui.stackedWidget_personas.setCurrentWidget(self.ui.personas_page_formulario)
            self.limpiar_formulario_personas()
            self.configurar_botones_personas("nuevo")

    def accion_personas_consultar(self):
        """Vuelve a la tabla, limpia filtros y recarga."""
        self.ui.stackedWidget_personas.setCurrentWidget(self.ui.personas_page_consulta)
        self.configurar_botones_personas("consultando")
        self.ui.filtro_personas_nombre.clear()
        self.ui.filtro_personas_tipo.setCurrentIndex(0)
        self.cargar_tabla_personas()

    def accion_personas_cancelar(self):
        """Cancela 'Nuevo' o 'Actualizar' y vuelve a la tabla."""
        self.accion_personas_consultar()

    def accion_personas_regresar(self):
        """Regresa al menú de inicio."""
        self.ui.stackedWidget.setCurrentWidget(self.ui.Inicio)
        if self.menu_esta_oculto:
            self.toggle_menu_main()

    def guardar_nueva_persona(self):
        """
        Valida el formulario de Personas y llama al db_manager
        para INSERTAR en mDtsPerson y mUsuario.
        """
        # 1. Validar que los campos de texto no estén vacíos
        campos_texto = {
            "Nombre": self.ui.txt_per_nombre,
            "Apellido Paterno": self.ui.txt_per_apepat,
            "Apellido Materno": self.ui.txt_per_apemat,
            "E-mail": self.ui.txt_per_email,
            "Login": self.ui.txt_per_login,
            "Password": self.ui.txt_per_password
        }
        for nombre_campo, widget in campos_texto.items():
            if not widget.text().strip():
                QMessageBox.warning(self, "Datos incompletos", f"El campo '{nombre_campo}' no puede estar vacío.")
                return

        # 2. Validar que los QComboBox hayan seleccionado algo
        if self.ui.combo_per_genero.currentIndex() <= 0:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un 'Género'.")
            return
        if self.ui.combo_per_puesto.currentIndex() <= 0:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un 'Puesto'.")
            return
        if self.ui.combo_per_tipopersona.currentIndex() <= 0:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un 'Tipo de Persona'.")
            return

        # 3. Validar que el Login no exista ya
        login_nuevo = self.ui.txt_per_login.text().strip()
        if self.db_manager.check_login_exists(login_nuevo):
            QMessageBox.warning(self, "Error", f"El login '{login_nuevo}' ya está en uso. Por favor, elija otro.")
            return

        # 4. Recopilar todos los datos en diccionarios
        fecha_nac = self.ui.date_per_fecnac.date()
        edad_calculada = self._calcular_edad(fecha_nac)

        datos_persona = {
            "Nombre": self.ui.txt_per_nombre.text().strip(),
            "ApePat": self.ui.txt_per_apepat.text().strip(),
            "ApeMat": self.ui.txt_per_apemat.text().strip(),
            "FecNac": fecha_nac.toString("yyyy-MM-dd"),
            "E_mail": self.ui.txt_per_email.text().strip(),
            "Telefono": self.ui.txt_per_telefono.text().strip(),
            "CvGenero": self.ui.combo_per_genero.currentData(),
            "CvPuesto": self.ui.combo_per_puesto.currentData(),
            "CvTpPerso": self.ui.combo_per_tipopersona.currentData(),
            "Edad": edad_calculada,  # <-- AÑADIDO (Tu idea)
            "RedSoc": "N/A"  # <-- AÑADIDO (El campo que faltaba)
        }

        datos_usuario = {
            "Login": login_nuevo,
            "Password": self.ui.txt_per_password.text(),  # ¡Recuerda hashear esto en un proyecto real!
            "FecIni": self.ui.date_per_fecini.date().toString("yyyy-MM-dd"),
            "FecVen": self.ui.date_per_fecven.date().toString("yyyy-MM-dd"),
            "EdoCta": self.ui.combo_per_edocta.currentText()
        }

        # 5. Enviar a la Base de Datos
        exito = self.db_manager.add_persona_y_usuario(
            datos_persona,
            datos_usuario,
            self.current_login
        )

        # 6. Informar y recargar
        if exito:
            QMessageBox.information(self, "Éxito", f"Usuario '{login_nuevo}' creado correctamente.")
            self.accion_personas_consultar()  # Volver a la tabla
        else:
            QMessageBox.critical(self, "Error de BD", "Error en la transacción. No se pudo crear el usuario.")

    def _calcular_edad(self, fecha_nacimiento):
        """Calcula la edad basada en un objeto QDate."""
        hoy = date.today()
        # Convierte QDate a date de datetime
        nac = fecha_nacimiento.toPyDate()

        # Calcula la edad
        edad = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))
        return edad

    def _set_combo_by_data(self, combobox, data_to_find):
        """
        Función auxiliar: Busca un ID (almacenado en currentData)
        en un QComboBox y lo selecciona.
        """
        if data_to_find is None:
            combobox.setCurrentIndex(0)
            return

        # findData busca en los datos (IDs) guardados, no en el texto visible
        index = combobox.findData(data_to_find)

        if index != -1:  # Si lo encontró
            combobox.setCurrentIndex(index)
        else:
            # Si no encuentra el ID (ej. ID 0 o nulo), pone "Seleccione..."
            combobox.setCurrentIndex(0)

    def accion_personas_actualizar(self):
        """
        Lógica del botón 'Actualizar/Guardar':
        - Si estamos consultando: Carga los datos en el formulario.
        - Si estamos actualizando: Guarda los datos en la BD.
        """
        if self.estado_actual_personas == "actualizando":
            # Si el estado es "actualizando", el botón dice "Guardar".
            self.guardar_actualizacion_persona()  # Llamamos a la nueva función de guardado
        else:
            # Si el estado es "consultando", el botón dice "Actualizar".
            self.cargar_datos_persona_en_formulario()

    def cargar_datos_persona_en_formulario(self):
        """
        Toma la fila seleccionada de la tabla de personas,
        obtiene todos sus datos de la BD y llena el formulario.
        """
        # 1. Obtener la fila seleccionada
        fila = self.ui.tabla_personas.currentRow()
        if fila == -1:
            # Esta comprobación ya la hace 'configurar_botones_personas',
            # pero es una doble seguridad.
            QMessageBox.warning(self, "Error", "No has seleccionado ninguna persona para actualizar.")
            return

        try:
            # 2. Obtener el ID de Usuario (CvUser) de la tabla (Columna 0)
            cv_user_item = self.ui.tabla_personas.item(fila, 0)
            cv_user_a_editar = int(cv_user_item.text())

            # 3. Llamar a la BD para obtener TODOS los datos
            datos = self.db_manager.get_persona_info_by_id(cv_user_a_editar)

            if not datos:
                QMessageBox.critical(self, "Error de BD",
                                     "No se pudieron recuperar los datos completos de esta persona.")
                return

            self.limpiar_formulario_personas()
            # 4. Guardar los IDs que estamos editando

            self.current_persona_id_edicion = cv_user_a_editar  # CvUser
            self.current_person_id_edicion = datos['CvPerson']


            self.ui.txt_per_nombre.setText(datos['DsNombre'])
            self.ui.txt_per_apepat.setText(datos['ApePat'])
            self.ui.txt_per_apemat.setText(datos['ApeMat'])
            self.ui.txt_per_email.setText(datos['E_mail'])
            self.ui.txt_per_telefono.setText(datos['Telefono'])
            self.ui.txt_per_login.setText(datos['Login'])
            self.ui.txt_per_password.setText(datos['Password'])

            # Seleccionar ComboBoxes usando el ID que guardamos
            self._set_combo_by_data(self.ui.combo_per_genero, datos['CvGenero'])
            self._set_combo_by_data(self.ui.combo_per_puesto, datos['CvPuesto'])
            self._set_combo_by_data(self.ui.combo_per_tipopersona, datos['CvTpPerso'])
            self.ui.combo_per_edocta.setCurrentText(datos['EdoCta'])

            # Cargar las fechas
            self.ui.date_per_fecnac.setDate(QDate.fromString(str(datos['FecNac']), "yyyy-MM-dd"))
            self.ui.date_per_fecini.setDate(QDate.fromString(str(datos['FecIni']), "yyyy-MM-dd"))
            self.ui.date_per_fecven.setDate(QDate.fromString(str(datos['FecVen']), "yyyy-MM-dd"))

            # 6. Cambiar de vista y de estado
            self.ui.stackedWidget_personas.setCurrentWidget(self.ui.personas_page_formulario)
            self.configurar_botones_personas("actualizando")

        except Exception as e:
            print(f"Error al leer los datos de la tabla: {e}")
            QMessageBox.critical(self, "Error", "No se pudieron cargar los datos de la fila seleccionada.")

    def guardar_actualizacion_persona(self):
        """Valida y guarda los datos de una persona MODIFICADA."""

        # 1. Obtener los IDs que estamos editando
        cv_user = self.current_persona_id_edicion
        cv_person = self.current_person_id_edicion

        if cv_user is None or cv_person is None:
            QMessageBox.critical(self, "Error", "Se perdió la referencia del usuario a editar. Acción cancelada.")
            return

        # 2. Validar campos (igual que en "Nuevo")
        campos_texto = {
            "Nombre": self.ui.txt_per_nombre,
            "Apellido Paterno": self.ui.txt_per_apepat,
            "Apellido Materno": self.ui.txt_per_apemat,
            "E-mail": self.ui.txt_per_email,
            "Login": self.ui.txt_per_login,
            "Password": self.ui.txt_per_password
        }
        for nombre_campo, widget in campos_texto.items():
            if not widget.text().strip():
                QMessageBox.warning(self, "Datos incompletos", f"El campo '{nombre_campo}' no puede estar vacío.")
                return
        if self.ui.combo_per_genero.currentIndex() <= 0:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un 'Género'.")
            return
        if self.ui.combo_per_puesto.currentIndex() <= 0:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un 'Puesto'.")
            return
        if self.ui.combo_per_tipopersona.currentIndex() <= 0:
            QMessageBox.warning(self, "Datos incompletos", "Debe seleccionar un 'Tipo de Persona'.")
            return

        # 3. Validar que el Login no exista (EXCLUYENDO al usuario actual)
        login_nuevo = self.ui.txt_per_login.text().strip()
        if self.db_manager.check_login_exists(login_nuevo, current_user_id=cv_user):
            QMessageBox.warning(self, "Error",
                                f"El login '{login_nuevo}' ya está en uso por otro usuario. Por favor, elija otro.")
            return

        # 4. Recopilar todos los datos (igual que en "Nuevo")
        fecha_nac = self.ui.date_per_fecnac.date()
        edad_calculada = self._calcular_edad(fecha_nac)
        datos_persona = {
            "Nombre": self.ui.txt_per_nombre.text().strip(),
            "ApePat": self.ui.txt_per_apepat.text().strip(),
            "ApeMat": self.ui.txt_per_apemat.text().strip(),
            "FecNac": fecha_nac.toString("yyyy-MM-dd"),
            "E_mail": self.ui.txt_per_email.text().strip(),
            "Telefono": self.ui.txt_per_telefono.text().strip(),
            "CvGenero": self.ui.combo_per_genero.currentData(),
            "CvPuesto": self.ui.combo_per_puesto.currentData(),
            "CvTpPerso": self.ui.combo_per_tipopersona.currentData(),
            "Edad": edad_calculada,
            "RedSoc": "N/A"  # Mantenemos este valor por defecto
        }

        datos_usuario = {
            "Login": login_nuevo,
            "Password": self.ui.txt_per_password.text(),
            "FecIni": self.ui.date_per_fecini.date().toString("yyyy-MM-dd"),
            "FecVen": self.ui.date_per_fecven.date().toString("yyyy-MM-dd"),
            "EdoCta": self.ui.combo_per_edocta.currentText()
        }

        # 5. Enviar a la Base de Datos (¡Llamamos a UPDATE!)
        exito = self.db_manager.update_persona_y_usuario(
            cv_user, cv_person,
            datos_persona,
            datos_usuario,
            self.current_login
        )

        # 6. Informar y recargar
        if exito:
            QMessageBox.information(self, "Éxito", f"Usuario '{login_nuevo}' actualizado correctamente.")
            self.accion_personas_consultar()  # Volver a la tabla
        else:
            QMessageBox.critical(self, "Error de BD", "Error en la transacción. No se pudo actualizar el usuario.")

    def accion_personas_borrar(self):
        """
        Toma la fila seleccionada de la tabla de personas,
        pide confirmación y la elimina.
        """
        # 1. Obtener la fila seleccionada
        fila = self.ui.tabla_personas.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "No has seleccionado ninguna persona para borrar.")
            return

        try:
            # 2. Obtener el ID de Usuario (CvUser) y el Nombre
            cv_user_item = self.ui.tabla_personas.item(fila, 0)
            cv_user_a_borrar = int(cv_user_item.text())

            nombre_item = self.ui.tabla_personas.item(fila, 2)  # Columna "Nombre Completo"
            nombre_a_borrar = nombre_item.text()

            # Seguridad: No permitas que el usuario se borre a sí mismo
            if cv_user_a_borrar == self.current_cv_user:
                QMessageBox.critical(self, "Acción denegada", "No puedes eliminar tu propia cuenta de usuario.")
                return

            # 3. Pedir confirmación al usuario (Regla de seguridad)
            confirmacion = QMessageBox.question(self, "Confirmar Eliminación",
                                                f"¿Estás seguro de que deseas eliminar permanentemente a:\n\n{nombre_a_borrar} (ID: {cv_user_a_borrar})?\n\nEsta acción también eliminará todos sus pagos, asistencias y evaluaciones asociadas.",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            # 4. Si el usuario confirma
            if confirmacion == QMessageBox.StandardButton.Yes:
                # 5. Llamar a la BD para eliminar
                exito = self.db_manager.delete_persona_y_usuario(cv_user_a_borrar, self.current_login)

                if exito:
                    QMessageBox.information(self, "Éxito", "El usuario ha sido eliminado correctamente.")
                    self.cargar_tabla_personas()  # Recargar la tabla
                else:
                    QMessageBox.critical(self, "Error de BD",
                                         "No se pudo eliminar el usuario. Revise la consola para más detalles.")

        except Exception as e:
            print(f"Error al borrar persona: {e}")
            QMessageBox.critical(self, "Error", "No se pudo obtener el ID de la persona a borrar.")

    # --- AÑADIDO: Funciones para los nuevos módulos ---

    def _configurar_botones_crud(self, estado, btn_nuevo, btn_actualizar, btn_borrar, btn_cancelar, btn_consultar):
        """
        Función genérica para configurar botones CRUD según las reglas de las imágenes.

        """
        # Estado "Consultando" (Inicial)
        if estado == "consultando":
            btn_nuevo.setText("Nuevo")
            btn_nuevo.setEnabled(True)
            btn_actualizar.setText("Actualizar")
            # Para esta demo simple, los habilitamos.
            # En una implementación real, dependerían de la selección de la tabla.
            btn_actualizar.setEnabled(True)
            btn_borrar.setText("Borrar")
            btn_borrar.setEnabled(True)
            btn_cancelar.setEnabled(False)
            btn_consultar.setEnabled(True)

        # Estado "Nuevo" (Clic en Nuevo)
        elif estado == "nuevo":
            btn_nuevo.setText("Guardar")  #
            btn_nuevo.setEnabled(True)
            btn_actualizar.setEnabled(False)  #
            btn_borrar.setEnabled(False)  #
            btn_cancelar.setEnabled(True)
            btn_consultar.setEnabled(True)

        # Estado "Actualizando" (Clic en Actualizar)
        elif estado == "actualizando":
            btn_nuevo.setEnabled(False)  #
            btn_actualizar.setText("Guardar")  #
            btn_actualizar.setEnabled(True)
            btn_borrar.setEnabled(False)  #
            btn_cancelar.setEnabled(True)
            btn_consultar.setEnabled(True)

        # Simulación de "Borrando"
        elif estado == "borrando":
            btn_nuevo.setEnabled(False)  #
            btn_actualizar.setEnabled(False)  #
            btn_borrar.setText("Borrar")  # El texto no cambia
            btn_borrar.setEnabled(True)
            btn_cancelar.setEnabled(True)
            btn_consultar.setEnabled(True)

    # =================================================================
    # === MÓDULO: CATÁLOGOS (Lógica de botones)
    # =================================================================

    def accion_catalogos_nuevo(self):
        # Si ya estamos en "nuevo", el botón es "Guardar".
        if self.estado_actual_catalogos == "nuevo":

            # --- LÍNEA AÑADIDA ---
            self.db_manager.registrar_acceso(self.current_login, True,
                                             "AUDITORIA BD: Se ha agregado un registro de un catalogo")
            # --- FIN DE LÍNEA AÑADIDA ---

            QMessageBox.information(self, "Simulación", "Acción 'Guardar Nuevo Catálogo' ejecutada (simulación).")
            self.accion_catalogos_consultar()  # Volvemos al inicio
        else:
            self.estado_actual_catalogos = "nuevo"
            # self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_2) # page_2 es el formulario
            QMessageBox.information(self, "Simulación", "Mostrando formulario para 'Nuevo Catálogo' (simulación).")
            self._configurar_botones_crud(
                self.estado_actual_catalogos,
                self.ui.btn_cata_nuevo, self.ui.btn_cata_actualizar, self.ui.btn_cata_borrar,
                self.ui.btn_cata_cancelar, self.ui.btn_cata_consultar
            )

    def accion_catalogos_actualizar(self):
        # Si estamos "actualizando", el botón es "Guardar".
        if self.estado_actual_catalogos == "actualizando":

            # --- LÍNEA AÑADIDA ---
            self.db_manager.registrar_acceso(self.current_login, True, "AUDITORIA BD: Se ha actualizado un registro de un catalogo")
            # --- FIN DE LÍNEA AÑADIDA ---

            QMessageBox.information(self, "Simulación",
                                    "Acción 'Guardar Actualización Catálogo' ejecutada (simulación).")
            self.accion_catalogos_consultar()  # Volvemos al inicio
        else:
            self.estado_actual_catalogos = "actualizando"
            # self.ui.stackedWidget_2.setCurrentWidget(self.ui.page_2)
            QMessageBox.information(self, "Simulación", "Cargando datos para 'Actualizar Catálogo' (simulación).")
            self._configurar_botones_crud(
                self.estado_actual_catalogos,
                self.ui.btn_cata_nuevo, self.ui.btn_cata_actualizar, self.ui.btn_cata_borrar,
                self.ui.btn_cata_cancelar, self.ui.btn_cata_consultar
            )

    def accion_catalogos_borrar(self):
        # Para cumplir la regla, deshabilitamos otros botones
        self.estado_actual_catalogos = "borrando"
        self._configurar_botones_crud(
            self.estado_actual_catalogos,
            self.ui.btn_cata_nuevo, self.ui.btn_cata_actualizar, self.ui.btn_cata_borrar,
            self.ui.btn_cata_cancelar, self.ui.btn_cata_consultar
        )

        # --- LÍNEA AÑADIDA ---
        self.db_manager.registrar_acceso(self.current_login, True, "AUDITORIA BD: Se ha eliminado un registro de un catalogo")
        # --- FIN DE LÍNEA AÑADIDA ---

        QMessageBox.information(self, "Simulación",
                                "Acción 'Borrar Catálogo' ejecutada (simulación). \nPresione Cancelar o Consultar para resetear.")

    def accion_catalogos_consultar(self):
        self.estado_actual_catalogos = "consultando"
        # Aquí iría el código para volver a la página de la tabla
        # self.ui.stackedWidget_2.setCurrentWidget(self.ui.page) # page es la tabla
        self._configurar_botones_crud(
            self.estado_actual_catalogos,
            self.ui.btn_cata_nuevo, self.ui.btn_cata_actualizar, self.ui.btn_cata_borrar,
            self.ui.btn_cata_cancelar, self.ui.btn_cata_consultar
        )

    # =================================================================
    # === MÓDULO: ASISTENCIA (Lógica de botones)
    # =================================================================

    def accion_asistencia_nuevo(self):
        if self.estado_actual_asistencia == "nuevo":

            # --- LÍNEA AÑADIDA ---
            self.db_manager.registrar_acceso(self.current_login, True, "AUDITORIA BD: Se ha agregado una asistencia")
            # --- FIN DE LÍNEA AÑADIDA ---

            QMessageBox.information(self, "Simulación", "Acción 'Guardar Nueva Asistencia' ejecutada (simulación).")
            self.accion_asistencia_consultar()
        else:
            self.estado_actual_asistencia = "nuevo"
            # self.ui.stackedWidget_3.setCurrentWidget(self.ui.page_4)
            QMessageBox.information(self, "Simulación", "Mostrando formulario para 'Nueva Asistencia' (simulación).")
            self._configurar_botones_crud(
                self.estado_actual_asistencia,
                self.ui.btn_asis_nuevo, self.ui.btn_asis_actualizar, self.ui.btn_asis_borrar,
                self.ui.btn_asis_cancelar, self.ui.btn_asis_consultar
            )

    def accion_asistencia_actualizar(self):
        if self.estado_actual_asistencia == "actualizando":

            # --- LÍNEA AÑADIDA ---
            self.db_manager.registrar_acceso(self.current_login, True, "AUDITORIA BD: Se ha actualizado una asistencia")
            # --- FIN DE LÍNEA AÑADIDA ---

            QMessageBox.information(self, "Simulación",
                                    "Acción 'Guardar Actualización Asistencia' ejecutada (simulación).")
            self.accion_asistencia_consultar()
        else:
            self.estado_actual_asistencia = "actualizando"
            # self.ui.stackedWidget_3.setCurrentWidget(self.ui.page_4)
            QMessageBox.information(self, "Simulación", "Cargando datos para 'Actualizar Asistencia' (simulación).")
            self._configurar_botones_crud(
                self.estado_actual_asistencia,
                self.ui.btn_asis_nuevo, self.ui.btn_asis_actualizar, self.ui.btn_asis_borrar,
                self.ui.btn_asis_cancelar, self.ui.btn_asis_consultar
            )

    def accion_asistencia_borrar(self):
        self.estado_actual_asistencia = "borrando"
        self._configurar_botones_crud(
            self.estado_actual_asistencia,
            self.ui.btn_asis_nuevo, self.ui.btn_asis_actualizar, self.ui.btn_asis_borrar,
            self.ui.btn_asis_cancelar, self.ui.btn_asis_consultar
        )

        # --- LÍNEA AÑADIDA ---
        self.db_manager.registrar_acceso(self.current_login, True, "AUDITORIA BD: Se ha eliminado una asistencia")
        # --- FIN DE LÍNEA AÑADIDA ---

        QMessageBox.information(self, "Simulación",
                                "Acción 'Borrar Asistencia' ejecutada (simulación). \nPresione Cancelar o Consultar para resetear.")

    def accion_asistencia_consultar(self):
        self.estado_actual_asistencia = "consultando"
        # self.ui.stackedWidget_3.setCurrentWidget(self.ui.page_3)
        self._configurar_botones_crud(
            self.estado_actual_asistencia,
            self.ui.btn_asis_nuevo, self.ui.btn_asis_actualizar, self.ui.btn_asis_borrar,
            self.ui.btn_asis_cancelar, self.ui.btn_asis_consultar
        )

    # =================================================================
    # === MÓDULO: EVALUACIONES (Lógica de botones)
    # =================================================================

    def accion_evaluaciones_nuevo(self):
        if self.estado_actual_evaluaciones == "nuevo":

            # --- LÍNEA AÑADIDA ---
            self.db_manager.registrar_acceso(self.current_login, True, "AUDITORIA BD: Se ha agregado una evaluacion")
            # --- FIN DE LÍNEA AÑADIDA ---

            QMessageBox.information(self, "Simulación", "Acción 'Guardar Nueva Evaluación' ejecutada (simulación).")
            self.accion_evaluaciones_consultar()
        else:
            self.estado_actual_evaluaciones = "nuevo"
            # self.ui.stackedWidget_4.setCurrentWidget(self.ui.page_6)
            QMessageBox.information(self, "Simulación", "Mostrando formulario para 'Nueva Evaluación' (simulación).")
            self._configurar_botones_crud(
                self.estado_actual_evaluaciones,
                self.ui.btn_eva_nuevo, self.ui.btn_eva_actualizar, self.ui.btn_eva_borrar,
                self.ui.btn_eva_cancelar, self.ui.btn_eva_consultar
            )

    def accion_evaluaciones_actualizar(self):
        if self.estado_actual_evaluaciones == "actualizando":

            # --- LÍNEA AÑADIDA ---
            self.db_manager.registrar_acceso(self.current_login, True, "AUDITORIA BD: Se ha actualizado una evaluacion")
            # --- FIN DE LÍNEA AÑADIDA ---

            QMessageBox.information(self, "Simulación",
                                    "Acción 'Guardar Actualización Evaluación' ejecutada (simulación).")
            self.accion_evaluaciones_consultar()
        else:
            self.estado_actual_evaluaciones = "actualizando"
            # self.ui.stackedWidget_4.setCurrentWidget(self.ui.page_6)
            QMessageBox.information(self, "Simulación", "Cargando datos para 'Actualizar Evaluación' (simulación).")
            self._configurar_botones_crud(
                self.estado_actual_evaluaciones,
                self.ui.btn_eva_nuevo, self.ui.btn_eva_actualizar, self.ui.btn_eva_borrar,
                self.ui.btn_eva_cancelar, self.ui.btn_eva_consultar
            )

    def accion_evaluaciones_borrar(self):
        self.estado_actual_evaluaciones = "borrando"
        self._configurar_botones_crud(
            self.estado_actual_evaluaciones,
            self.ui.btn_eva_nuevo, self.ui.btn_eva_actualizar, self.ui.btn_eva_borrar,
            self.ui.btn_eva_cancelar, self.ui.btn_eva_consultar
        )

        # --- LÍNEA AÑADIDA ---
        self.db_manager.registrar_acceso(self.current_login, True, "AUDITORIA BD: Se a eliminado una evaluacion")
        # --- FIN DE LÍNEA AÑADIDA ---

        QMessageBox.information(self, "Simulación",
                                "Acción 'Borrar Evaluación' ejecutada (simulación). \nPresione Cancelar o Consultar para resetear.")

    def accion_evaluaciones_consultar(self):
        self.estado_actual_evaluaciones = "consultando"
        # self.ui.stackedWidget_4.setCurrentWidget(self.ui.page_5)
        self._configurar_botones_crud(
            self.estado_actual_evaluaciones,
            self.ui.btn_eva_nuevo, self.ui.btn_eva_actualizar, self.ui.btn_eva_borrar,
            self.ui.btn_eva_cancelar, self.ui.btn_eva_consultar
        )

    # --- FIN DE AÑADIDO ---