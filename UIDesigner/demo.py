# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 15:18:45 2019

@author: Dave
"""
def scan(status,erro,window,running,semafaro):
    from scpiinterface import Instrument, manager
    unidades = {"kHz": 1000,
                "MHz": 1000000}
    while(True):
        semafaro.acquire()
        minn = window.box_frequencia_min.value()
        maxx = window.box_frequencia_max.value()
        step = window.box_step.value()
        print("eaemen")
        unidade_max = unidades[str(window.box_unidade_final.currentText())]
        unidade_min = unidades[str(window.box_unidade_inicial.currentText())]
        unidade_step = unidades[str(window.box_unidade_step.currentText())]
        print(step * unidade_step)
        start = minn * unidade_min
        end = maxx * unidade_max
        erro.setText(" ")
        try:
    
            instrument = Instrument()
            instrument.activate_mode_receiver()
            instrument.receiver_set_step(step * unidade_step)
            if (start) > (end):
                erro.setText("Erro: min é menor que max.")
                return
            for freq in range(start,end,step * unidade_step):
                if running.is_set():
                # Set and read levels from 200kHz to 10MHz in receiver mode
                    instrument.write('RMOD:FREQ {}'.format(freq))
                    print(instrument.receiver_frequency)
                    print(instrument.receiver_level)
                else:
                    status.setText("Esperando")
                    erro.setText("Interrompido")
                    instrument.close()
                    raise Exception
    
    
            print(instrument.hello)
    
            instrument.close()
            status.setText("Esperando")
            erro.setText(" ")
            running.clear()
    
        except (KeyboardInterrupt, Exception) as e:
            print("Something went wrong: " + str(e))
            try:
                instrument.close()
            except AttributeError:
                pass
            running.clear()
    
