# This Python file uses the following encoding: utf-8
import sys,os
import PySide2

import threading
from threading import Thread, active_count

from PySide2.QtCore import QAbstractTableModel
import PySide2.QtCore as QtCore
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QApplication, QMainWindow
from PySide2.QtCore import QFile
from PySide2.QtCore import Slot
from PySide2.QtWidgets import QItemDelegate
from demo import scan
from detector import detect
from analisador import scan
from datetime import datetime


class AlignDelegate(QItemDelegate):
    def paint(self, painter, option, index):
        option.displayAlignment = QtCore.Qt.AlignCenter
        QItemDelegate.paint(self, painter, option, index)

class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, mylist, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.mylist[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != QtCore.Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            try: 
                return self.header[col]
            except IndexError:
                print("ue")
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return str(col + 1)
        return None
    
    def update_data(self, dataIn):
        self.mylist = dataIn
        self.dataChanged.emit(len(self.mylist[0]),len(self.mylist))
        
    def update_header(self, dataIn):
        column = len(dataIn)
        row = self.rowCount(self.parent) 
        self.header = dataIn
        self.beginInsertColumns(self.index(row,column), 1, len(self.header)-2)
        
        self.endInsertColumns()
        self.headerDataChanged.emit(QtCore.Qt.Horizontal,len(dataIn),0)

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
        header = [chr(x+65) for x in range(0,14)]
        data_list = [['?'] * 13 for x in range(0,13) ]
        self.table_model = MyTableModel(janela.interface, data_list, header)
        
        detectorThread = Thread(name='detect',target=detect,args=(window.interface,semafaro_detector,running_detector))
        scannerThread = Thread(name='scan',target=scan,args=(window.interface,running_detector,interrupt_scanner,semafaro_scanner,semafaro_detector,self.table_model))
        detectorThread.start()
        scannerThread.start()
        janela.interface.box_nome.setText("arquivo_" + datetime.now().strftime("%d-%m-%Y %H-%M-%S"))
        janela.interface.tableView.setModel(self.table_model)
        janela.interface.tableView.setItemDelegate(AlignDelegate())
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
    