# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 15:18:45 2019

@author: Dave
"""


class Interrupt_Error(Exception):
        pass

def instrument_clean_up(instrument,interface,detector,error_msg=" ",):
    instrument.close()
    interface.label_status.setText("Esperando")
    interface.label_erro.setText(error_msg)
    detector.release()

def read_level_at_freq(instrument,freq):
    instrument.write('RMOD:FREQ {}'.format(freq))
    return instrument.receiver_level

def interrupt_instrument(instrument,interface):
    interface.label_status.setText("Esperando")
    interface.label_erro.setText("Interrompido")
    instrument.close()
    raise Interrupt_Error

def scan(interface,running,interrupt,semafaro,detector):
    from scpiinterface import Instrument
    unidades = {"kHz": 1000,
                "MHz": 1000000,
                "GHz": 1000000000}
    while(True):
        semafaro.acquire()
        if running.is_set() is False:
            return
        interface.botao_vai.setEnabled(False)
        interface.botao_parar.setEnabled(True)
        interface.botao_instrumento.setEnabled(False)
        interface.label_status.setText("Escaneando...")
        interface.label_erro.setText(" ")
        
        print("eaemen")
        unidade = unidades[str(interface.box_frequencia_unidade.currentText())]
        freq = interface.box_frequencia.value() * unidade
        indiceX = interface.box_dimensao_X.value()
        indiceY = interface.box_dimensao_Y.value()
        
        try:
            instrument = Instrument(interface.box_instrumento.currentText())
            instrument.activate_mode_receiver()
            print("total:{}".format(indiceX*indiceY))
            for i in range(0,indiceX):
                if running.is_set() is False:
                        return
                if interrupt.is_set() is False:
                    read_level_at_freq(instrument,freq)
                else:
                    print(interrupt_instrument(instrument,interface))
                for j in range(0,indiceY):
                    if running.is_set() is False:
                        return
                    if interrupt.is_set() is False:
                        print(read_level_at_freq(instrument,freq))
                    else:
                        interrupt_instrument(instrument,interface)  

            print(instrument.hello)
            instrument_clean_up(instrument,interface,detector)
            
    
        except (KeyboardInterrupt, Interrupt_Error) as e:
            print("Something went wrong: " + str(e))
            try:
                if running.is_set() is False:
                        return
                instrument_clean_up(instrument,interface,detector, "Erro: Interrompido.")
            except Exception:
                interface.label_status.setText("Esperando")
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
                interface.label_status.setText("Esperando")
                interface.label_erro.setText("Erro: Cheque Conexão.")
                if running.is_set() is False:
                            return
        interface.botao_vai.setEnabled(True)
        interface.botao_parar.setEnabled(False)
        interface.botao_instrumento.setEnabled(True)