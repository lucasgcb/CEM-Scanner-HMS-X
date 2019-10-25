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
from analisador import scan
class janela(QMainWindow):
    def __init__(self):
        loader = QUiLoader()
        dirname = os.path.dirname(os.path.abspath(__file__))
        os.chdir(dirname)
        ui_file = QFile("dialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.interface = loader.load(ui_file)
        ui_file.close()

class Gerente:
    def __init__(self,app,janela):
        self.app = app
        self.runners = []
        self.semaphores = []
        running_detector = threading.Event()
        running_detector.set()
        interrupt_scanner = threading.Event()
        interrupt_scanner.set()
        semafaro_detector = threading.Semaphore(1)
        semafaro_scanner = threading.Semaphore(0)
        self.runners.append(running_detector)
        self.semaphores.append(semafaro_detector)
        self.semaphores.append(semafaro_scanner)
        self.janela = janela 
        self.janela.interface.show()
        self.janela.interface.botao_parar.setEnabled(False)
        detectorThread = Thread(name='detect',target=detect,args=(window.interface,semafaro_detector,running_detector))
        scannerThread = Thread(name='scan',target=scan,args=(window.interface,running_detector,interrupt_scanner,semafaro_scanner,semafaro_detector))
        detectorThread.start()
        scannerThread.start()
        @Slot()
        def go():
            interrupt_scanner.clear()
            semafaro_scanner.release()

        @Slot()
        def stop():
            
            self.janela.interface.label_status.setText("Interrompendo...")
            interrupt_scanner.set()
        
        @Slot()
        def detecting():
            pass
            semafaro_detector.release()

        
        self.janela.interface.botao_vai.clicked.connect(go)
        self.janela.interface.botao_parar.clicked.connect(stop)
        self.janela.interface.botao_instrumento.clicked.connect(detecting)
        

    def exec(self):
        self.app.exec_()
        self.clean_up()
    def clean_up(self):
        print("CLEAN EXIT")
        for runner in self.runners:
            runner.clear()
        
        for semaphore in self.semaphores:
            semaphore.release()
    

if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    window = janela()
    gerente = Gerente(app,window)
    gerente.exec()
    