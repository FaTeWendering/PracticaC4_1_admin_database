from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QDialog
from .ui_ControlWindows import Ui_Dialog



class ControlWindows(QDialog):
    sesion_cerrada = pyqtSignal()
    def __init__(self, db_manager):
        super().__init__()

        self.db_manager = db_manager
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.menu_ancho_original = self.ui.frame_4.maximumWidth()
        self.menu_esta_oculto = False
        self.animacion_menu = None

        self.ui.btn_cerrar.clicked.connect(self.close)
        self.ui.btn_minimizar.clicked.connect(self.showMinimized)
        self.ui.btn_maximizar.clicked.connect(self.Maximizar)

        self.ui.btn_usuarios.clicked.connect(self.mostrar_pagina_usuarios)
        self.ui.btn_Personas.clicked.connect(self.mostrar_pagina_personas)
        self.ui.btn_productos.clicked.connect(self.mostrar_pagina_productos)
        self.ui.btn_cerrarsesion.clicked.connect(self.cerrar_sesion)

        self.ui.btn_toggle_menu.clicked.connect(self.toggle_menu)
        self.ui.btn_toggle_menu.setText("<")

        self.dragging = False
        self.offset = None

    def Maximizar(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def mostrar_pagina_usuarios(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page)

    def mostrar_pagina_personas(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_2)

    def mostrar_pagina_productos(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.page_3)

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

    def set_user_info(self, nombre_completo, puesto, genero):
        """Actualiza el QLabel de bienvenida con el nombre, puesto y género."""

        # Lógica para determinar el saludo
        saludo = "Bienvenido(a)"  # Saludo por defecto
        if genero.lower() == 'masculino':
            saludo = "Bienvenido"
        elif genero.lower() == 'femenino':
            saludo = "Bienvenida"

        texto_bienvenida = f"{saludo}:\n{nombre_completo}\n({puesto})"
        self.ui.lbl_bienvenida.setText(texto_bienvenida)
    def toggle_menu(self):
        if self.animacion_menu and self.animacion_menu.state() == QPropertyAnimation.State.Running:
            return

        if self.menu_esta_oculto:
            ancho_inicio = 0
            ancho_fin = self.menu_ancho_original
            self.ui.btn_toggle_menu.setText("<")
            self.menu_esta_oculto = False
        else:
            ancho_inicio = self.ui.frame_4.width()
            ancho_fin = 0
            self.ui.btn_toggle_menu.setText("☰")
            self.menu_esta_oculto = True

        self.animacion_menu = QPropertyAnimation(self.ui.frame_4, b"maximumWidth")

        self.animacion_menu.setDuration(300)

        self.animacion_menu.setStartValue(ancho_inicio)
        self.animacion_menu.setEndValue(ancho_fin)

        self.animacion_menu.setEasingCurve(QEasingCurve.Type.InOutCubic)

        self.animacion_menu.start()

    def cerrar_sesion(self):
        self.ui.lbl_bienvenida.setText("Bienvenido(a):")
        self.sesion_cerrada.emit()