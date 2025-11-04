from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import pyqtSignal
from datetime import datetime
from PyQt6.QtCore import Qt, QSize
from .ui_LoginWindows import Ui_Dialog


class LoginWindow(QWidget):
    login_exitoso = pyqtSignal(str, str, str, str, str)
    def __init__(self, db_manager):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.db_manager = db_manager
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.close)
        self.ui.pushButton_2.clicked.connect(self.toggle_maximize)
        self.ui.pushButton_3.clicked.connect(self.showMinimized)

        self.ui.btn_aceptar.clicked.connect(self.on_aceptar_clicked)
        self.ui.btn_cancel.clicked.connect(self.limpiar)

        self.ui.txt_password.setEchoMode(self.ui.txt_password.EchoMode.Password)
        self.ui.btn_ver.clicked.connect(self.Mostrar_password)

        self.ui.btn_Salir.clicked.connect(self.close)

    def Mostrar_password(self):
        if self.ui.txt_password.echoMode() == self.ui.txt_password.echoMode().Normal:
            self.ui.txt_password.setEchoMode(self.ui.txt_password.echoMode().Password)
        else:
            self.ui.txt_password.setEchoMode(self.ui.txt_password.EchoMode.Normal)

    def ocultar_password(self):
        self.ui.txt_password.setEchoMode(self.ui.txt_password.EchoMode.Password)
        
    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint()
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.isMaximized():
            return

        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, 'drag_position'):
            new_position = event.globalPosition().toPoint()
            self.move(new_position - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if hasattr(self, 'drag_position'):
                del self.drag_position
                del self.offset
        super().mouseReleaseEvent(event)

    def limpiar(self):
        self.ui.txt_login.clear()
        self.ui.txt_password.clear()

    def on_aceptar_clicked(self):
        login = self.ui.txt_login.text()
        password = self.ui.txt_password.text()

        if not login or not password:
            QMessageBox.warning(self, "Error", "Debe completar ambos campos.")
            self.db_manager.registrar_acceso(login, False, "Intento fallido: Campos vacios")
            return

        db_data = self.db_manager.validar_usuario(login, password)

        if db_data is None:
            QMessageBox.critical(self, "Error de Sistema",
                                 "Fallo al obtener respuesta de la base de datos. Verifique la conexión o el SQL.")
            self.db_manager.registrar_acceso(login, False, "Error de conexion/SQL en validacion")
            return

        if db_data == -1:
            QMessageBox.critical(self, "Acceso denegado", "Credenciales inválidas (Usuario o Contraseña incorrectos).")
            self.db_manager.registrar_acceso(login, False,"Intento fallido Credenciales invalidas")
            self.ui.txt_login.clear()
            self.ui.txt_password.clear()
            return

        try:
            (cv_user, edocta_str, fecini_str, fecven_str,
             nombre, ape_pat, ape_mat, puesto, genero) = db_data

            fecini = datetime.strptime(fecini_str, '%Y-%m-%d').date()
            fecven = datetime.strptime(fecven_str, '%Y-%m-%d').date()
            fecha_actual = datetime.now().date()

        except (ValueError, TypeError) as e:
            QMessageBox.critical(self, "Error de Datos",
                                 f"El formato de datos devuelto por la base de datos es incorrecto. Error: {e}")
            self.db_manager.registrar_acceso(login, False, f"Error de formato de datos {e}")
            return

        if fecha_actual > fecven and edocta_str.lower() == 'false':
            QMessageBox.warning(self,"Acceso denegado","Cuenta caducada")
            self.db_manager.registrar_acceso(login, False, "Intento fallido: Cuenta caducada y deshabilitada")
            self.ui.txt_login.clear()
            self.ui.txt_password.clear()
            return

        if edocta_str.lower() == 'false':
            QMessageBox.warning(self, "Acceso denegado",
                                "Cuenta desabilitada")
            self.db_manager.registrar_acceso(login, False, "Intento fallido: Cuenta deshabilitada('False')")
            self.ui.txt_login.clear()
            self.ui.txt_password.clear()
            return

        if fecha_actual > fecven:
            exito_update = self.db_manager.actualizar_estado_cuenta(cv_user, 'False')
            Detalle = "Intento fallido: Cuenta vencida(Actualizada a ('False')" if exito_update else "Intento fallido: Cuenta vencida (Error al actualizar)"
            QMessageBox.critical(self, "Acceso denegado", "Cuenta vencida")
            self.db_manager.registrar_acceso(login, False, Detalle)
            self.ui.txt_login.clear()
            self.ui.txt_password.clear()
            return

        if fecha_actual < fecini:
            QMessageBox.warning(self, "Acceso denegado",
                                "Cuenta por activarse.")
            self.db_manager.registrar_acceso(login, False, "Intento Fallido: Cuenta por activarse")
            self.ui.txt_login.clear()
            self.ui.txt_password.clear()
            return
        nombre_completo = f"{nombre} {ape_pat} {ape_mat}"
        puesto_str = puesto if puesto else "N/A" # Manejar si no tiene puesto
        genero_str = genero if genero else "N/A"

        self.db_manager.registrar_acceso(login, True, "Login exitoso")

        self.login_exitoso.emit(nombre_completo, puesto_str, genero_str, login, password)
        self.hide()