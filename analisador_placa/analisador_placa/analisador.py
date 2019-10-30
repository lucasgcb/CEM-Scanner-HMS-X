# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 15:18:45 2019

@author: Dave
"""
import time
import datetime

class Interrupt_Error(Exception):
        pass

def instrument_clean_up(instrument,interface,detector,error_msg=" ",):
    instrument.close()
    interface.label_status.setText("Esperando")
    interface.label_erro.setText(error_msg)
    detector.release()
    interface_scan_finished(interface)

def interrupt_instrument(instrument,interface):
    interface.label_status.setText("Esperando")
    interface.label_erro.setText("Interrompido")
    instrument.close()
    raise Interrupt_Error

def interface_scan_start(interface):
    interface.botao_vai.setEnabled(False)
    interface.botao_parar.setEnabled(True)
    interface.botao_instrumento.setEnabled(False)
    interface.box_nome.setEnabled(False)
    interface.label_erro.setText(" ")
    interface.label_status.setText("Iniciando...")

def instrument_setup(Instrument,freq,interface):
    instrument = Instrument(interface.box_instrumento.currentText())
    instrument.activate_mode_receiver()
    instrument.write('RMOD:FREQ {}'.format(freq))
    time.sleep(0.5)
    interface.label_status.setText("Escaneando...")
    return instrument

def interface_scan_finished(interface):
    interface.botao_vai.setEnabled(True)
    interface.botao_parar.setEnabled(False)
    interface.botao_instrumento.setEnabled(True)
    interface.box_nome.setEnabled(True)

def dim_gen(indiceX,char):
    return [char for y in range(0,indiceX)]

def scan(interface,running,interrupt,semafaro,detector,model):
    from scpiinterface import Instrument
    import csv
    unidades = {"kHz": 1000,
                "MHz": 1000000,
                "GHz": 1000000000}
                
    while(True):
        semafaro.acquire()
        interface_scan_start(interface)
        if running.is_set() is False:
            return
        
        unidade = unidades[str(interface.box_frequencia_unidade.currentText())]
        freq = interface.box_frequencia.value() * unidade
        indiceX = interface.box_dimensao_X.value()
        indiceY = interface.box_dimensao_Y.value()
        
        try:
            fname= interface.box_nome.text()
            
            with open('{}.csv'.format(fname), 'w', newline='') as csvfile:
                spamwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                header = [chr(x+65) for x in range(0,indiceX)]
                data_list = [dim_gen(indiceX,'?') for Y in range(0,indiceY)]
                model.update_header(header)
                model.update_data(data_list)
                spamwriter.writerow(header)
                instrument = instrument_setup(Instrument,freq,interface)
                print("total:{}".format(indiceX*indiceY))
                for i in range(0,indiceY):
                    #interface.label_colunas.setText(" ".join(header))
                    row = []
                    if running.is_set() is False:
                            return
                    if interrupt.is_set():
                        interrupt_instrument(instrument,interface)
                    for j in range(0,indiceX):
                        if running.is_set() is False:
                            return
                        if interrupt.is_set() is False:
                            val = instrument.receiver_level
                            row.append(val)
                            data_list[i][j] = val
                            model.update_data(data_list)
                            #interface.label_linhas.setText(" ".join(progress))
                        else:
                            interrupt_instrument(instrument,interface)  
                    spamwriter.writerow(row)

            print(instrument.hello)
            instrument_clean_up(instrument,interface,detector)
            
    
        except (KeyboardInterrupt, Interrupt_Error) as e:
            print("Something went wrong: " + str(e))
            try:
                if running.is_set() is False:
                        return
                instrument_clean_up(instrument,interface,detector, "Erro: Interrompido.")
            except Exception:
                interface.label_erro.setText("Erro: Cheque Conexão.")
                if running.is_set() is False:
                            return
        
        except Exception as e:
            print("Something went wrong: " + str(e))
            try:
                if running.is_set() is False:
                        return
                instrument_clean_up(instrument,interface,detector, "Erro: Desconhecido. Cheque conexão.")
            except Exception:
                interface.label_erro.setText("Erro: Cheque Conexão.")
                if running.is_set() is False:
                            return
       
        interface.box_nome.setText("arquivo_" + datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S"))