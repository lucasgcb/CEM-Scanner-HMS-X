from interfacehandlers import (get_filename, interface_error_msg, interface_update_filename,
                              interface_matrix_end, interface_matrix_start, get_commander_port,
                              interface_status_msg)
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from PySide2.QtCore import Slot
import cmdrinterface

#### a fazer: COLOCAR ESSA JOÇA EM THREAD PRA N TRAVAR DEPOIS DO JOVEM METER 999 EM UNIDADE E MORRER

class Programmer:
    def __init__(self):
        self.interface = None
    def programmer(self):
        loader = QUiLoader()
        interface_matrix_start(self.interface)
        ui_file = QFile("program.ui")
        ui_file.open(QFile.ReadOnly)
        self.wid = loader.load(ui_file)
        ui_file.close()
        self.wid.setWindowTitle('Calibrador')
        self.wid.show()
        self.wid.installEventFilter(self)
        
        try:
            self.cmdr = cmdrinterface.Commander(get_commander_port(self.interface))
            self.cmdr.connect()
            interface_status_msg(self.wid, "Conectado.")
            self.stepX = self.cmdr.stepX
            self.stepY = self.cmdr.stepY
            self.wid.box_stepX.setValue(self.stepX)
            self.wid.box_stepY.setValue(self.stepY)
        except Exception:
            interface_status_msg(self.wid, "Algo deu errado.")
        @Slot()
        def up():
            interface_status_msg(self.wid, "MOVENDO +Y")
            try:
                self.cmdr.move_Y(1,self.wid.box_stepY.value())
                interface_status_msg(self.wid, "Conectado.")
            except Exception:
                interface_status_msg(self.wid, "Algo deu errado.")
            
        @Slot()
        def down():
            interface_status_msg(self.wid, "MOVENDO -Y")
            try:
                self.cmdr.move_Y(-1,self.wid.box_stepY.value())
                interface_status_msg(self.wid, "Conectado.")
            except Exception:
                interface_status_msg(self.wid, "Algo deu errado.")
        @Slot()
        def right():
            interface_status_msg(self.wid, "MOVENDO +X")
            try:
                self.cmdr.move_X(1,self.wid.box_stepX.value())
                interface_status_msg(self.wid, "Conectado.")
            except Exception:
                interface_status_msg(self.wid, "Algo deu errado.")
        @Slot()
        def left():
            interface_status_msg(self.wid, "MOVENDO -X")
            try:
                self.cmdr.move_X(-1,self.wid.box_stepX.value())
                interface_status_msg(self.wid, "Conectado.")
            except Exception:
                interface_status_msg(self.wid, "Algo deu errado.")
        @Slot()
        def done():
            self.cmdr.set_stepX(self.wid.box_stepX.value())
            self.cmdr.set_stepY(self.wid.box_stepY.value())
            self.cmdr.close()
            self.wid.close()
        @Slot()
        def cancelar():
            ### Resetar para os valores antes da programação.
            self.cmdr.set_stepX(self.stepX)
            self.cmdr.set_stepY(self.stepY)
            self.cmdr.close()
            self.wid.close()

        self.wid.botao_up.clicked.connect(up)
        self.wid.botao_right.clicked.connect(right)
        self.wid.botao_left.clicked.connect(left)
        self.wid.botao_down.clicked.connect(down)
        self.wid.botao_ok.clicked.connect(done)
        self.wid.botao_cancelar.clicked.connect(done)

    def mover(self):
        loader = QUiLoader()
        interface_matrix_start(self.interface)
        ui_file = QFile("mover.ui")
        ui_file.open(QFile.ReadOnly)
        self.mvr = loader.load(ui_file)
        ui_file.close()
        self.mvr.setWindowTitle('Mover')
        self.mvr.show()
        self.mvr.installEventFilter(self)
        
        try:
            self.cmdr = cmdrinterface.Commander(get_commander_port(self.interface))
            self.cmdr.connect()
            interface_status_msg(self.mvr, "Conectado.")
        except Exception:
            interface_status_msg(self.mvr, "Algo deu errado.")
        @Slot()
        def up():
            interface_status_msg(self.mvr, "MOVENDO +Y")
            try:
                self.cmdr.move_Y(self.mvr.box_unidadeY.value())
                interface_status_msg(self.mvr, "Conectado.")
            except Exception:
                interface_status_msg(self.mvr, "Algo deu errado.")
            
        @Slot()
        def down():
            interface_status_msg(self.mvr, "MOVENDO -Y")
            try:
                self.cmdr.move_Y(-self.mvr.box_unidadeY.value())
                interface_status_msg(self.mvr, "Conectado.")
            except Exception:
                interface_status_msg(self.mvr, "Algo deu errado.")
        @Slot()
        def right():
            interface_status_msg(self.mvr, "MOVENDO +X")
            try:
                self.cmdr.move_X(self.mvr.box_unidadeX.value())
                interface_status_msg(self.mvr, "Conectado.")
            except Exception:
                interface_status_msg(self.mvr, "Algo deu errado.")
        @Slot()
        def left():
            interface_status_msg(self.mvr, "MOVENDO -X")
            try:
                self.cmdr.move_X(-self.mvr.box_unidadeX.value())
                interface_status_msg(self.mvr, "Conectado.")
            except Exception:
                interface_status_msg(self.mvr, "Algo deu errado.")
        @Slot()
        def done():
            self.cmdr.close()
            self.mvr.close()

        self.mvr.botao_up.clicked.connect(up)
        self.mvr.botao_right.clicked.connect(right)
        self.mvr.botao_left.clicked.connect(left)
        self.mvr.botao_down.clicked.connect(down)
        self.mvr.botao_ok.clicked.connect(done)