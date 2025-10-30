from PyQt6.QtCore import Qt, pyqtSignal
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

        self.ui.btn_cerrar.clicked.connect(self.close)
        self.ui.btn_minimizar.clicked.connect(self.showMinimized)
        self.ui.btn_maximizar.clicked.connect(self.Maximizar)

        self.ui.btn_usuarios.clicked.connect(self.mostrar_pagina_usuarios)
        self.ui.btn_Personas.clicked.connect(self.mostrar_pagina_personas)
        self.ui.btn_productos.clicked.connect(self.mostrar_pagina_productos)
        self.ui.btn_cerrarsesion.clicked.connect(self.cerrar_sesion)

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

    def set_user_info(self, nombre_completo, puesto):
        """Actualiza el QLabel de bienvenida con el nombre y puesto."""
        texto_bienvenida = f"Bienvenido(a):\n{nombre_completo}\n({puesto})"
        self.ui.lbl_bienvenida.setText(texto_bienvenida)

    def cerrar_sesion(self):
        self.ui.lbl_bienvenida.setText("Bienvenido(a):")
        self.sesion_cerrada.emit()