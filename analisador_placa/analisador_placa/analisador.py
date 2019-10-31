# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 15:18:45 2019

@author: Dave
"""
import time
import datetime

class Interrupt_Error(Exception):
        pass

def interface_error_msg(interface, error_msg="Erro: Desconhecido"):
    interface.label_erro.setText(error_msg)

def interface_status_msg(interface, status_msg="Desconhecido"):
    interface.label_status.setText(status_msg)

def instrument_clean_up(instrument,interface,detector,error_msg=" ",):
    instrument.close()
    interface_status_msg(interface,"Esperando")
    interface_error_msg(interface,error_msg)
    detector.release()
    interface_scan_finished(interface)

def interrupt_instrument(instrument,interface):
    interface_status_msg(interface,"Esperando")
    interface_error_msg(interface,"Interrompido")
    instrument.close()
    raise Interrupt_Error

def interface_scan_start(interface):
    interface.botao_vai.setEnabled(False)
    interface.botao_parar.setEnabled(True)
    interface.botao_instrumento.setEnabled(False)
    interface.box_nome.setEnabled(False)
    ###
    interface_error_msg(interface," ")
    interface_status_msg(interface,"Iniciando...")

def instrument_setup(Instrument,freq,interface):
    instrument = Instrument(interface.box_instrumento.currentText())
    instrument.activate_mode_receiver()
    instrument.write('RMOD:FREQ {}'.format(freq))
    time.sleep(0.5)
    ###
    interface_status_msg(interface,"Escaneando...")
    return instrument

def interface_scan_finished(interface):
    interface_update_filename(interface)
    interface.botao_vai.setEnabled(True)
    interface.botao_parar.setEnabled(False)
    interface.botao_instrumento.setEnabled(True)
    interface.box_nome.setEnabled(True)

def get_unit(interface):
    unidades = {"kHz": 1000,
                "MHz": 1000000,
                "GHz": 1000000000}
    return unidades[str(interface.box_frequencia_unidade.currentText())]

def get_frequency(interface):
    freq = interface.box_frequencia.value()
    return freq * get_unit(interface)

def interface_update_filename(interface):
    interface.box_nome.setText("arquivo_" + datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S"))

def get_X(interface):
    return interface.box_dimensao_X.value()

def get_Y(interface):
    return interface.box_dimensao_Y.value()

def dim_gen(indiceX,char):
    return [char for y in range(0,indiceX)]

def get_filename(interface):
    return interface.box_nome.text()

def model_to_csv(model,fname,interface):
    import csv  
    with open('{}.csv'.format(fname), 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(model.get_header())
        data = model.get_data()
        for row in data:
            rows = []
            for val in row:
                rows.append(val)
            spamwriter.writerow(row)
    interface_update_filename(interface)

def scan(interface,running,interrupt,semafaro,detector,model):
    from scpiinterface import Instrument
    while(True):
        semafaro.acquire()
        if running.is_set() is False:
            return
        try:
            freq = get_frequency(interface)
            indiceX = get_X(interface)
            indiceY = get_Y(interface)
            fname= get_filename(interface)
            interface_scan_start(interface)
            ####
            header = [chr(x+65) for x in range(0,indiceX)]
            data_list = [dim_gen(indiceX,'?') for Y in range(0,indiceY)]
            model.update_header(header)
            model.update_data(data_list)
            
            instrument = instrument_setup(Instrument,freq,interface)
            print("total:{}".format(indiceX*indiceY))
            for i in range(0,indiceY):
                if running.is_set() is False:
                        return
                if interrupt.is_set():
                    interrupt_instrument(instrument,interface)
                for j in range(0,indiceX):
                    if running.is_set() is False:
                        return
                    if interrupt.is_set() is False:
                        val = instrument.receiver_level
                        data_list[i][j] = str(val)
                        model.update_data(data_list)
                    else:
                        interrupt_instrument(instrument,interface)  
            print(instrument.hello)
            instrument_clean_up(instrument,interface,detector)
            model_to_csv(model,fname,interface)
    
        except (KeyboardInterrupt, Interrupt_Error) as e:
            print("Something went wrong: " + str(e))
            try:
                if running.is_set() is False:
                        return
                instrument_clean_up(instrument,interface,detector, "Erro: Interrompido.")
            except Exception:
                interface_error_msg(interface, "Erro: Cheque Conexão.")
                if running.is_set() is False:
                            return
        
        except Exception as e:
            print("Something went wrong: " + str(e))
            try:
                if running.is_set() is False:
                        return
                instrument_clean_up(instrument,interface,detector, "Erro: Desconhecido. Cheque conexão.")
            except Exception:
                interface_error_msg(interface,"Erro: Cheque Conexão.")
                if running.is_set() is False:
                            return
        interface_scan_finished(interface)