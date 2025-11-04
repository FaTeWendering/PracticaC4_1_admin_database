import sys
from PyQt6.QtWidgets import QApplication
from db.databaseManager import DatabaseManager
from Gui.LoginWindows import LoginWindow
from Gui.ControlWindows import ControlWindows

class MainApplication():
    def __init__(self):
        self.db_manager = DatabaseManager(
            host='localhost',
            user='root',
            password='321f4899721M56_',
            database='bdPracticaC4_1'
        )
        self.login_win = LoginWindow(self.db_manager)
        self.control_win = ControlWindows(self.db_manager)
        self.login_win.login_exitoso.connect(self.mostrar_control)
        self.control_win.sesion_cerrada.connect(self.mostrar_login)

    def run(self):
        self.login_win.show()

    def mostrar_control(self, nombre_completo, puesto, genero, login, password):
        self.control_win.set_user_info(nombre_completo, puesto, genero, login, password)
        self.control_win.show()

    def mostrar_login(self):
        self.control_win.hide()
        self.login_win.ui.txt_password.clear()
        self.login_win.ui.txt_login.clear()
        self.login_win.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_app = MainApplication()
    main_app.run()
    sys.exit(app.exec())