# This Python file uses the following encoding: utf-8
import sys,os
import PySide2


from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QFile
from PySide2.QtCore import Slot
from PySide2 import QtGui
from threading import Thread, active_count
import threading
from demo import scan

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dirname = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dirname)
    print(os.getcwd())
    ui_file = QFile("xablau.ui")
    ui_file.open(QFile.ReadOnly)

    loader = QUiLoader()
    window = loader.load(ui_file)

    ui_file.close()
    window.show()

    label_erro = window.label_erro
    label_status = window.label_status
    running = threading.Event()
    running.clear()
    semafaro = threading.Semaphore(0)
    print(semafaro)
    scannerThread = Thread(name='scan',target=scan,args=(label_status, label_erro,
                                                          window,running,semafaro))
    
    scannerThread.start()

    @Slot()
    def say_hello():
     for t in threading.enumerate():
        if running.is_set():
         label_erro.setText("Erro: Scan ainda em Progresso")
         return
     label_status.setText("Escaneando...")
     running.set()
     semafaro.release()

    @Slot()
    def stop():
        label_erro.setText("Parando...")
        running.clear()

    window.botao_scan.clicked.connect(say_hello)
    window.botao_scan_stop.clicked.connect(stop)

    sys.exit(app.exec_())
