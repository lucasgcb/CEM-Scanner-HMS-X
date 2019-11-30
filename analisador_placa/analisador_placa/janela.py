# This Python file uses the following encoding: utf-8
import sys,os
import PySide2
from programmer import Programmer
import threading
from threading import Thread, active_count
import cmdrinterface
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
from interfacehandlers import (get_filename, interface_error_msg, interface_update_filename,
                              interface_matrix_end, interface_matrix_start, get_commander_port,
                              interface_status_msg)
from utility import model_to_csv

class AlignDelegate(QItemDelegate):
    """
    Esta função está ligada a tabela.
    - paint: define um estilo de alinhamento para o texto.
    - setEditorData: Coloca o dado do modelo interno no espaço para edição.
    """
    def paint(self, painter, option, index):
        option.displayAlignment = QtCore.Qt.AlignCenter
        QItemDelegate.paint(self, painter, option, index)
    def setEditorData(self, editor, index):
        text = index.data(PySide2.QtCore.Qt.EditRole) or index.data(PySide2.QtCore.Qt.DisplayRole)
        editor.setText(text)    
class MyTableModel(QtCore.QAbstractTableModel):
    def __init__(self, parent, mylist, header, *args):
        QtCore.QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header

    def flags(self, index):
        """
        Define as flags Qt para cada item.
        """
        return PySide2.QtCore.Qt.ItemIsEditable | PySide2.QtCore.Qt.ItemIsEnabled | PySide2.QtCore.Qt.ItemIsSelectable | PySide2.QtCore.Qt.ItemIsUserCheckable

    def setData(self, index, value, role=PySide2.QtCore.Qt.EditRole):
        """
        Atualiza valores do modelo em indices sendo editados.
        """
        if role == QtCore.Qt.EditRole:
            x = index.row()
            y = index.column()
            self.mylist[x][y] = value
            self.dataChanged.emit(len(self.mylist[0]),len(self.mylist))
            return True
        return False

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

    def get_data(self):
        return self.mylist
    def get_header(self):
        return self.header

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

class janela(QMainWindow, Programmer):
    def __init__(self):
        loader = QUiLoader()
        dirname = os.path.dirname(os.path.abspath(__file__))
        os.chdir(dirname)
        ui_file = QFile("dialog.ui")
        ui_file.open(QFile.ReadOnly)
        self.interface = loader.load(ui_file)
        ui_file.close()
        super(janela, self).__init__()

    def eventFilter(self, obj, event):
        if (obj is self.wid or obj is self.mvr) and event.type() == QtCore.QEvent.Close:
            interface_matrix_end(self.interface)
            try:
                self.cmdr.close()
            except Exception:
                pass
            return True
        try:
            return super(janela, self).eventFilter(obj, event)
        except RuntimeError:
            return True

class Gerente:
    def __init__(self,app,janela):
        DEFAULT_X = 13
        DEFAULT_Y = 13
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
        header = [chr(x+65) for x in range(0,DEFAULT_X)]
        data_list = [['?'] * DEFAULT_X for Y in range(0,DEFAULT_Y-1) ]
        self.table_model = MyTableModel(janela.interface, data_list, header)
        
        detectorThread = Thread(name='detect',target=detect,args=(janela.interface,semafaro_detector,running_detector))
        scannerThread = Thread(name='scan',target=scan,args=(janela.interface,running_detector,interrupt_scanner,semafaro_scanner,semafaro_detector,self.table_model))
        detectorThread.start()
        scannerThread.start()
        janela.interface.box_nome.setText("arquivo_" + datetime.now().strftime("%d-%m-%Y %H-%M-%S"))
        janela.interface.tableView.setModel(self.table_model)
        janela.interface.tableView.setItemDelegate(AlignDelegate())
        janela.interface.tableView.setShowGrid(True)

        @Slot()
        def go():
            interface_update_filename(self.janela.interface)
            interrupt_scanner.clear()
            semafaro_scanner.release()
        @Slot()
        def stop():
            interface_error_msg(self.janela.interface,"Interrompendo...")
            
            interrupt_scanner.set()
        
        @Slot()
        def detecting():
            pass
            semafaro_detector.release()

        @Slot()
        def salvar_manual():
            fname = get_filename(self.janela.interface)
            model_to_csv(self.table_model,fname)
            interface_error_msg(self.janela.interface,"Salvo: " + fname + ".csv")

        @Slot()
        def conf_matriz():
            self.janela.programmer()

        @Slot()
        def conf_posicao():
            self.janela.mover()

        self.janela.interface.botao_vai.clicked.connect(go)
        self.janela.interface.botao_parar.clicked.connect(stop)
        self.janela.interface.botao_matriz.clicked.connect(conf_matriz)
        self.janela.interface.botao_instrumento.clicked.connect(detecting)
        self.janela.interface.botao_salvar.clicked.connect(salvar_manual)
        self.janela.interface.botao_mover.clicked.connect(conf_posicao)
        

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
    