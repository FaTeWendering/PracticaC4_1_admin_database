from PyQt6.QtCore import (
    Qt, pyqtSignal, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup
)
from PyQt6.QtGui import QMouseEvent, QIcon
from PyQt6.QtWidgets import QDialog, QHeaderView, QLineEdit, QMessageBox
import re
from .ui_ControlWindows import Ui_Dialog


class ControlWindows(QDialog):
    sesion_cerrada = pyqtSignal()

    def __init__(self, db_manager):
        super().__init__()

        self.db_manager = db_manager
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.current_login = None
        self.current_password = None
        tabla_compras = self.ui.Table_compra
        header = tabla_compras.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        try:
            ruta_icono = "Gui/../../../../../../pyqt6/Imagenes/eye_on_see_show_view_vision_watch_icon_123215.png"
            eye_icono = QIcon(ruta_icono)

            self.ui.txt_pass_anterior.setEchoMode(QLineEdit.EchoMode.Password)
            eye_action_anterior = self.ui.txt_pass_anterior.addAction(eye_icono, QLineEdit.ActionPosition.TrailingPosition)
            eye_action_anterior.triggered.connect(
                lambda: self.toggle_password_visibility(self.ui.txt_pass_anterior)
            )

            self.ui.txt_pass_nuevo.setEchoMode(QLineEdit.EchoMode.Password)
            eye_action_nuevo = self.ui.txt_pass_nuevo.addAction(eye_icono, QLineEdit.ActionPosition.TrailingPosition)
            eye_action_nuevo.triggered.connect(
                lambda: self.toggle_password_visibility(self.ui.txt_pass_nuevo)
            )

            self.ui.txt_pass_repetir.setEchoMode(QLineEdit.EchoMode.Password)
            eye_action_repetir = self.ui.txt_pass_repetir.addAction(eye_icono, QLineEdit.ActionPosition.TrailingPosition)
            eye_action_repetir.triggered.connect(
                lambda: self.toggle_password_visibility(self.ui.txt_pass_repetir)
            )
        except AttributeError as e:
            print(f"ADVERTENCIA: No se pudieron crear los botones de ojo ¿Regeneraste el ui? Error: {e}")
        except Exception as e:
            print(f"Error inesperado configurando botones de ojo: {e}")

        self.menu_ancho_desplegado = 220
        self.menu_esta_oculto = False
        self.animacion_grupo_main = None

        self.ui.frame_4.setMinimumWidth(self.menu_ancho_desplegado)
        self.ui.frame_4.setMaximumWidth(self.menu_ancho_desplegado)

        self.compras_menu_ancho = 180
        self.compras_menu_oculto = False
        self.animacion_grupo_compras = None

        self.ui.frame_10.setMinimumWidth(self.compras_menu_ancho)
        self.ui.frame_10.setMaximumWidth(self.compras_menu_ancho)

        self.ui.btn_cerrar.clicked.connect(self.close)
        self.ui.btn_minimizar.clicked.connect(self.showMinimized)
        self.ui.btn_maximizar.clicked.connect(self.Maximizar)
        self.ui.btn_toggle_menu.clicked.connect(self.toggle_menu_main)
        self.ui.btn_toggle_menu.setText("<")

        self.ui.btn_catalogos.clicked.connect(self.mostrar_pagina_catalogos)
        self.ui.btn_Personas.clicked.connect(self.mostrar_pagina_personas)
        self.ui.btn_productos.clicked.connect(self.mostrar_pagina_pedido)
        self.ui.pushButton.clicked.connect(self.mostrar_pagina_recepped)
        self.ui.pushButton_2.clicked.connect(self.mostrar_pagina_compra)
        self.ui.pushButton_3.clicked.connect(self.mostrar_pagina_venta)
        self.ui.pushButton_4.clicked.connect(self.mostrar_pagina_cambiarpass)
        self.ui.btn_cerrarsesion.clicked.connect(self.cerrar_sesion)

        self.ui.btn_desplegar_menu_compras.clicked.connect(self.toggle_menu_compras)

        self.dragging = False
        self.offset = None


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

    def mostrar_pagina_venta(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_6)
        except AttributeError as e:
            print(f"Error: La pagina 'page_6' (venta) no existe. creela en Qt Designer.")

    def mostrar_pagina_cambiarpass(self):
        try:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_7)
            self.limpiar_campos_password()
            self.ui.btn_aceptar_pass.clicked.connect(self.procesar_cambio_password)
            self.ui.btn_cancel_pass.clicked.connect(self.limpiar_campos_password)
        except AttributeError as e:
            print(f"Error: La pagina 'page_7' (CambiarPass) no existe. creela en Qt Designer.")


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
            self.ui.btn_desplegar_menu_compras.setText(">")
            self.compras_menu_oculto = False
        else:
            self.ui.btn_desplegar_menu_compras.setText("<")
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
        self.ui.lbl_user_compra.setText(f"User: {nombre_completo}\n({puesto})")

        self.current_login = login
        self.current_password = password

    def toggle_password_visibility(self, line_edit_widget):
        if line_edit_widget.echoMode() == line_edit_widget.EchoMode.Password:
            line_edit_widget.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            line_edit_widget.setEchoMode(QLineEdit.EchoMode.Password)

    def procesar_cambio_password(self):
        password_anterior = self.ui.txt_pass_anterior.text()
        password_nuevo = self.ui.txt_pass_nuevo.text()
        password_repetir = self.ui.txt_pass_repetir.text()

        login_actual = self.current_login
        password_actual_guardado = self.current_password

        # --- INICIO DE VALIDACIONES ---

        # 1. Validar que la contraseña anterior sea correcta
        if not password_actual_guardado == password_anterior:
            QMessageBox.warning(self, "Acción denegada",
                                "La contraseña anterior no es igual a la ingresada.")
            self.limpiar_campos_password()
            return

        # 2. Validar que los campos no estén vacíos
        if not password_nuevo or not password_repetir:
            QMessageBox.warning(self, "Error", "El campo 'Password Nuevo' y 'Repetir' no pueden estar vacíos.")
            self.limpiar_campos_password()
            return

        # 3. Validar que las nuevas contraseñas no coincidan
        if password_nuevo != password_repetir:
            QMessageBox.warning(self, "Error", "Las nuevas contraseñas no coinciden.")
            self.limpiar_campos_password()
            return

        # 4. Validar que la nueva no sea igual a la anterior
        if password_nuevo == password_actual_guardado:
            QMessageBox.warning(self, "Error", "La nueva contraseña no puede ser igual a la anterior.")
            self.limpiar_campos_password()
            return

        # 5. Validar criterios del PDF (4-10 chars, 1 mayús, 1 min, 1 num, 1 especial)
        if not (4 <= len(password_nuevo) <= 10):
            QMessageBox.warning(self, "Error", "La contraseña debe tener entre 4 y 10 caracteres.")
            self.limpiar_campos_password()
            return
        if not re.search(r"[A-Z]", password_nuevo):
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos una mayúscula.")
            self.limpiar_campos_password()
            return
        if not re.search(r"[a-z]", password_nuevo):
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos una minúscula.")
            self.limpiar_campos_password()
            return
        if not re.search(r"[0-9]", password_nuevo):
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos un número.")
            self.limpiar_campos_password()
            return
        if not re.search(r"[\+\*\#\%]", password_nuevo):
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos un caracter especial (+, *, #, %).")
            self.limpiar_campos_password()
            return

        # 6. Validar que la nueva contraseña no exista en la BD
        if self.db_manager.verificar_password_existente(password_nuevo):
            QMessageBox.warning(self, "Error", "Esa contraseña ya está en uso por otro usuario. Elija una diferente.")
            self.limpiar_campos_password()
            return

        # --- FIN DE VALIDACIONES ---

        # 7. Si todo es correcto, actualizar la BD
        exito = self.db_manager.actualizar_password(login_actual, password_nuevo)

        if exito:
            QMessageBox.information(self, "Éxito", "¡Contraseña actualizada correctamente!")
            # Actualizamos la contraseña guardada en memoria
            self.current_password = password_nuevo
            self.limpiar_campos_password()
        else:
            QMessageBox.critical(self, "Error de Base de Datos", "No se pudo actualizar la contraseña.")


    def limpiar_campos_password(self):
        self.ui.txt_pass_anterior.clear()
        self.ui.txt_pass_nuevo.clear()
        self.ui.txt_pass_repetir.clear()

    def cerrar_sesion(self):
        self.ui.lbl_bienvenida.setText("Bienvenido(a):")
        self.sesion_cerrada.emit()