def interface_error_msg(interface, error_msg="Erro: Desconhecido"):
    interface.label_erro.setText(error_msg)

def interface_status_msg(interface, status_msg="Desconhecido"):
    interface.label_status.setText(status_msg)

def interface_scan_start(interface):
    interface.botao_vai.setEnabled(False)
    interface.botao_parar.setEnabled(True)
    interface.botao_instrumento.setEnabled(False)
    interface.box_nome.setEnabled(False)
    interface.botao_salvar.setEnabled(False)
    ###
    interface_error_msg(interface," ")
    interface_status_msg(interface,"Iniciando...")

def interface_matrix_start(interface):
    interface.botao_vai.setEnabled(False)
    interface.botao_parar.setEnabled(False)
    interface.botao_instrumento.setEnabled(False)
    interface.box_nome.setEnabled(False)
    interface.botao_salvar.setEnabled(False)
    interface.box_config.setEnabled(False)
    ###
    interface_error_msg(interface," ")
    interface_status_msg(interface,"Programando...")

def interface_matrix_end(interface):
    interface.botao_vai.setEnabled(True)
    interface.botao_parar.setEnabled(False)
    interface.botao_instrumento.setEnabled(True)
    interface.box_nome.setEnabled(True)
    interface.botao_salvar.setEnabled(True)
    interface.box_config.setEnabled(True)
    ###
    interface_error_msg(interface," ")
    interface_status_msg(interface,"Esperando")

def interface_scan_finished(interface):
    interface_update_filename(interface)
    interface.botao_vai.setEnabled(True)
    interface.botao_parar.setEnabled(False)
    interface.botao_instrumento.setEnabled(True)
    interface.box_nome.setEnabled(True)
    interface.botao_salvar.setEnabled(True)

def get_unit(interface):
    unidades = {"kHz": 1000,
                "MHz": 1000000,
                "GHz": 1000000000}
    return unidades[str(interface.box_frequencia_unidade.currentText())]

def get_frequency(interface):
    freq = interface.box_frequencia.value()
    return freq * get_unit(interface)

def interface_update_filename(interface):
    import datetime
    interface.box_nome.setText("arquivo_" + datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S"))

def get_X(interface):
    return interface.box_dimensao_X.value()

def get_Y(interface):
    return interface.box_dimensao_Y.value()

def get_filename(interface):
    return interface.box_nome.text()