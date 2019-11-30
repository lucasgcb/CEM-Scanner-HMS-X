# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 15:18:45 2019

@author: Dave
"""
import time
from cmdrinterface import Commander
from utility import model_to_csv
from interfacehandlers import (interface_status_msg, interface_error_msg, 
                               interface_scan_finished, get_frequency, 
                               get_filename, get_unit, get_X, get_Y, 
                               interface_scan_start, interface_update_filename, get_commander_port)

class Interrupt_Error(Exception):
        pass

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

def retornar(interface,commander,indiceX,indiceY):
    if interface.check_return.isChecked():
        interface_status_msg(interface, "Voltando...")
        
        if(indiceY % 2 == 0):
            ## Se o numero de linhas for par, então já está no final.
            commander.move_X(-indiceX)
        commander.move_Y(indiceY)

def extrair_recurso(texto):
    ### Extrai o nome do recurso do combobox
    import re 
    return re.search(r'(\w*::\w*)', texto).group(0)

def instrument_setup(Instrument,freq,interface):
    instrument = Instrument(extrair_recurso(interface.box_instrumento.currentText()))
    instrument.activate_mode_receiver()
    instrument.write('RMOD:FREQ {}'.format(freq))
    time.sleep(0.5)
    ###
    interface_status_msg(interface,"Escaneando...")
    return instrument

def commander_setup(Commander,interface):
    cmdr = Commander(get_commander_port(interface))
    cmdr.connect()
    return cmdr

def commander_cleanup(cmdr_handle,interface):
    try:
        cmdr_handle.close()
    except Exception:
        pass
    return

def dim_gen(indiceX,char):
    return [char for y in range(0,indiceX)]


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
            direcao = 1
            instrument = instrument_setup(Instrument,freq,interface)
            commander = commander_setup(Commander,interface)
            print("total:{}".format(indiceX*indiceY))
            for i in range(0,indiceY):
                if(i!=0):
                    commander.move_Y(-1)
                if running.is_set() is False:
                        return
                if interrupt.is_set():
                    interrupt_instrument(instrument,interface)
                if indiceX == 1:
                    data_list[i][j] = str(val)
                    model.update_data(data_list)
                for j in range(0,indiceX):
                    if running.is_set() is False:
                        return
                    if interrupt.is_set() is False:
                        val = instrument.receiver_level
                        if(i % 2 == 0):
                            data_list[i][j] = str(val)
                            direcao = 1
                        else:
                            # Se esta linha for impar, faça de tras pra frente
                            data_list[i][-(j+1)] = str(val)
                            direcao = -1
                        model.update_data(data_list)
                        if(j!=indiceX-1):
                            ## Se for o ultimo da coluna, nao mova
                            commander.move_X(direcao)
                    else:
                        interrupt_instrument(instrument,interface)  
            print(instrument.hello)
            retornar(interface,commander,j,i)
            commander_cleanup(commander,interface)
            instrument_clean_up(instrument,interface,detector)
            model_to_csv(model,fname)
            interface_error_msg(interface,"Salvo: " + fname + ".csv")
    
        except (KeyboardInterrupt, Interrupt_Error) as e:
            print("Something went wrong: " + str(e))
            try:
                if running.is_set() is False:
                        return
                commander_cleanup(commander,interface)
                instrument_clean_up(instrument,interface,detector, "Erro: Interrompido.")
            except Exception:
                interface_error_msg(interface, "Erro: Cheque Conexão.")
                interface_status_msg(interface, "Esperando...")
                if running.is_set() is False:
                            return
        
        except Exception as e:
            print("Something went wrong: " + str(e))
            try:
                if running.is_set() is False:
                        return
                commander_cleanup(commander,interface)
                instrument_clean_up(instrument,interface,detector, "Erro: Desconhecido. Cheque conexão.")
            except Exception:
                interface_error_msg(interface,"Erro: Cheque Conexão.")
                interface_status_msg(interface, "Esperando...")
                if running.is_set() is False:
                            return
        interface_scan_finished(interface)