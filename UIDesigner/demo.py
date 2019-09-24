# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 15:18:45 2019

@author: Dave
"""
def scan(status,erro,min,max,step,running):
    from scpiinterface import Instrument, manager
    unidade_max = 1000000
    unidade_min = 1000
    unidade_step = 1000
    start = min * unidade_min
    end = max * unidade_max

    erro.setText(" ")
    try:

        instrument = Instrument()
        instrument.activate_mode_receiver()
        instrument.receiver_set_step(step * unidade_step)
        if (start) > (end):
            erro.setText("Erro: min é menor que max.")
            return
        for freq in range(start,end,int(instrument.receiver_step)):
            if running.is_set():
            # Set and read levels from 200kHz to 10MHz in receiver mode
                instrument.write('RMOD:FREQ {}'.format(freq))
                print(instrument.receiver_frequency)
                print(instrument.receiver_level)
            else:
                status.setText("Esperando")
                erro.setText("Interrompido")
                raise Exception


        print(instrument.hello)

        instrument.close()
        status.setText("Esperando")
        erro.setText(" ")
        return

    except (KeyboardInterrupt, Exception) as e:
        print("Something went wrong: " + str(e))
        try:
            instrument.close()
        except AttributeError:
            pass

        manager.close()

        return
