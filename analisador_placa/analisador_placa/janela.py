# This Python file uses the following encoding: utf-8
import sys,os
import PySide2

import threading
from threading import Thread, active_count

import PySide2.QtCore as QtCore
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile
from PySide2.QtCore import Slot
from demo import scan
from detector import detect
class janela(QMainWindow):
    def __init__(self):
        loader = QUiLoader()
        dirname = os.path.dirname(os.path.abspath(__file__))
        os.chdir(dirname)
        ui_file = QFile("dialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.interface = loader.load(ui_file)
        ui_file.close()

if __name__ == "__main__":
   

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    running_detector = threading.Event()
    running_detector.clear()
    semafaro_detector = threading.Semaphore(1)

    window = janela()
    window.interface.show()

    detectorThread = Thread(name='detect',target=detect,args=(window.interface,semafaro_detector))
    detectorThread.start()
    @Slot()
    def go():
        pass
    
    @Slot()
    def detecting():
        semafaro_detector.release()

    
    window.interface.botao_vai.clicked.connect(go)
    window.interface.botao_instrumento.clicked.connect(detecting)
    
    sys.exit(app.exec_())
