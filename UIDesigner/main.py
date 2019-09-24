# This Python file uses the following encoding: utf-8
import sys,os
import PySide2

dirname = os.path.dirname(PySide2.__file__)
plugin_path = os.path.join(dirname, 'plugins', 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

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
    val_min = window.box_frequencia_min.value()
    val_max = window.box_frequencia_max.value()
    val_step = window.box_step.value()
    print(val_step)
    running = threading.Event()
    scannerThread = Thread(name='scan',target=scan,args=(label_status, label_erro,
                                                          val_min,val_max,val_step,running))

    @Slot()
    def say_hello():
     for t in threading.enumerate():
        if t.getName() =="scan":
         label_erro.setText("Erro: Scan ainda em Progresso")
     else:
        label_status.setText("Escaneando...")
        running.set()
        scannerThread.start()

    @Slot()
    def stop():
        running.clear()

    window.botao_scan.clicked.connect(say_hello)
    window.botao_scan_stop.clicked.connect(stop)

    sys.exit(app.exec_())
