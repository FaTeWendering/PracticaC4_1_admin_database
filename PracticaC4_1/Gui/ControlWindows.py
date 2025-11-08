import re
from PyQt6.QtCore import (
    Qt, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup
)
from PyQt6.QtGui import QMouseEvent, QIcon
from PyQt6.QtWidgets import QDialog, QHeaderView, QLineEdit, QMessageBox
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

        # --- AJUSTE DE LA TABLA DE COMPRAS ---
        tabla_compras = self.ui.Table_compra
        header = tabla_compras.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Descripción
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Cant
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Precio
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # SubTotal

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
        self.ui.frame_10.setMinimumWidth(self.compras_menu_ancho)
        self.ui.frame_10.setMaximumWidth(self.compras_menu_ancho)

        # --- CONEXIONES DE BOTONES DE LA VENTANA ---
        self.ui.btn_cerrar.clicked.connect(self.close)
        self.ui.btn_minimizar.clicked.connect(self.showMinimized)
        self.ui.btn_maximizar.clicked.connect(self.Maximizar)
        self.ui.btn_toggle_menu.clicked.connect(self.toggle_menu_main)
        self.ui.btn_toggle_menu.setText("<")

        # --- CONEXIONES DE BOTONES DEL MENÚ PRINCIPAL ---
        self.ui.btn_catalogos.clicked.connect(self.mostrar_pagina_catalogos)
        self.ui.btn_Personas.clicked.connect(self.mostrar_pagina_personas)
        self.ui.btn_productos.clicked.connect(self.mostrar_pagina_pedido)
        self.ui.pushButton.clicked.connect(self.mostrar_pagina_recepped)
        self.ui.pushButton_2.clicked.connect(self.mostrar_pagina_compra)
        self.ui.pushButton_3.clicked.connect(self.mostrar_pagina_venta)
        self.ui.pushButton_4.clicked.connect(self.mostrar_pagina_cambiarpass)
        self.ui.btn_cerrarsesion.clicked.connect(self.cerrar_sesion)

        # --- CONEXIONES DE LA PÁGINA DE COMPRAS ---
        self.ui.btn_desplegar_menu_compras.clicked.connect(self.toggle_menu_compras)
        self.ui.btn_nuevo_compras.clicked.connect(self.compras_boton_nuevo)
        self.ui.btn_actualizar_compras.clicked.connect(self.compras_boton_actualizar)
        self.ui.btn_borrar_compras.clicked.connect(self.compras_boton_borrar)
        self.ui.btn_cancelar_compras.clicked.connect(self.compras_boton_cancelar)

        self.dragging = False
        self.offset = None

        self.actualizar_estado_botones_compras()

    # --- MÓDULO: NAVEGACIÓN DE PÁGINAS ---

    def mostrar_pagina_catalogos(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)

    def mostrar_pagina_personas(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)

    def mostrar_pagina_pedido(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_3)

    def mostrar_pagina_recepped(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_4)

    def mostrar_pagina_compra(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_5)
        self.compras_boton_cancelar()

    def mostrar_pagina_venta(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_6)
        except AttributeError as e:
            print(f"Error: La pagina 'page_6' (venta) no existe. creela en Qt Designer.")

    def mostrar_pagina_cambiarpass(self):
        try:
            # Asumiendo que se llama 'page_7'
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_7)
            self.limpiar_campos_password()

            try:
                self.ui.btn_aceptar_pass.clicked.disconnect()
                self.ui.btn_cancel_pass.clicked.disconnect()
            except TypeError:
                pass

            self.ui.btn_aceptar_pass.clicked.connect(self.procesar_cambio_password)
            self.ui.btn_cancel_pass.clicked.connect(self.limpiar_campos_password)
        except AttributeError as e:
            print(f"Error: La pagina 'page_7' (CambiarPass) no existe. creela en Qt Designer. {e}")

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

    def toggle_menu_compras(self):
        if self.animacion_grupo_compras and self.animacion_grupo_compras.state() == QParallelAnimationGroup.State.Running:
            return

        ancho_fin = 0
        if self.compras_menu_oculto:
            ancho_fin = self.compras_menu_ancho
            self.ui.btn_desplegar_menu_compras.setText("<")  # Flecha izquierda
            self.compras_menu_oculto = False
        else:
            self.ui.btn_desplegar_menu_compras.setText(">")  # Flecha derecha
            self.compras_menu_oculto = True

        self.animacion_min_c = QPropertyAnimation(self.ui.frame_10, b"minimumWidth")
        self.animacion_max_c = QPropertyAnimation(self.ui.frame_10, b"maximumWidth")
        self.animacion_min_c.setDuration(300)
        self.animacion_min_c.setEndValue(ancho_fin)
        self.animacion_min_c.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animacion_max_c.setDuration(300)
        self.animacion_max_c.setEndValue(ancho_fin)
        self.animacion_max_c.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.animacion_grupo_compras = QParallelAnimationGroup()
        self.animacion_grupo_compras.addAnimation(self.animacion_min_c)
        self.animacion_grupo_compras.addAnimation(self.animacion_max_c)
        self.animacion_grupo_compras.start()

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

    def set_user_info(self, nombre_completo, puesto, genero, login, password):
        saludo = "Bienvenido(a)"
        if genero.lower() == 'masculino':
            saludo = "Bienvenido"
        elif genero.lower() == 'femenino':
            saludo = "Bienvenida"

        texto_bienvenida = f"{saludo}:\n{nombre_completo}\n({puesto})"
        self.ui.lbl_bienvenida.setText(texto_bienvenida)
        self.ui.lbl_user_compra.setText(f"User: {nombre_completo}")

        self.current_login = login
        self.current_password = password

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

    # --- MÓDULO: LÓGICA DE COMPRAS (CRUD) ---

    def actualizar_estado_botones_compras(self):
        """Habilita o deshabilita los botones de Compras según el estado."""

        if self.estado_compras == "navegando":
            self.ui.btn_nuevo_compras.setText("Nuevo")
            self.ui.btn_nuevo_compras.setEnabled(True)
            self.ui.btn_actualizar_compras.setText("Actualizar")
            self.ui.btn_actualizar_compras.setEnabled(True)
            self.ui.btn_borrar_compras.setEnabled(True)
            self.ui.btn_consulta_compras.setEnabled(True)
            self.ui.btn_regresar_compras.setEnabled(True)
            self.ui.btn_cancelar_compras.setEnabled(False)

        elif self.estado_compras == "insertando" or self.estado_compras == "modificando":
            if self.estado_compras == "insertando":
                self.ui.btn_nuevo_compras.setText("Guardar")
                self.ui.btn_nuevo_compras.setEnabled(True)
                self.ui.btn_actualizar_compras.setEnabled(False)
            else:  # modificando
                self.ui.btn_nuevo_compras.setEnabled(False)
                self.ui.btn_actualizar_compras.setText("Guardar")
                self.ui.btn_actualizar_compras.setEnabled(True)

            self.ui.btn_borrar_compras.setEnabled(False)
            self.ui.btn_consulta_compras.setEnabled(False)
            self.ui.btn_regresar_compras.setEnabled(False)
            self.ui.btn_cancelar_compras.setEnabled(True)

    def compras_boton_nuevo(self):
        if self.estado_compras == "insertando":
            print("Lógica para GUARDAR un nuevo registro de compra...")
            self.estado_compras = "navegando"
        else:
            print("Cambiando a modo INSERCIÓN de compra.")
            self.estado_compras = "insertando"
            # self.limpiar_campos_compras()
        self.actualizar_estado_botones_compras()

    def compras_boton_actualizar(self):
        if self.estado_compras == "modificando":
            print("Lógica para GUARDAR un registro de compra actualizado...")
            self.estado_compras = "navegando"
        else:
            print("Cambiando a modo MODIFICACIÓN de compra.")
            self.estado_compras = "modificando"
        self.actualizar_estado_botones_compras()

    def compras_boton_borrar(self):
        print("Lógica para BORRAR registro de compra...")
        pass

    def compras_boton_cancelar(self):
        print("Operación cancelada, volviendo a modo navegación.")
        self.estado_compras = "navegando"
        self.actualizar_estado_botones_compras()