def identificar(gerente,recurso,interface):
    import serial
    import re
    inst = gerente.open_resource(recurso)
    try:
        identificador = inst.query("*IDN?").split(',')
        if(identificador[0]=="HAMEG" and identificador[1]=="HMS-X"):
            interface.box_instrumento.addItem("HAMEG HMS-X (" + str(recurso) + ")")
        else:
            ## Tentar serial se tiver uma resposta, mas que está estranha
            inst.close()
            porta_do_recurso = re.search('(COM\d*)',str(recurso)).group(0)
            ser = serial.Serial(porta_do_recurso)
            ser.write(b'*IDN?')     # write a string
            identificador = [ser.readline()]
            ser.close()
            if(identificador[0]==b"CMDR!\n"):
                interface.box_controlador.addItem("Comandante (" + str(recurso) + ")")
        inst.close()
    except Exception:
        ## Não atende o requerimento da API VISA.. tentar comunicar serial direto msm
        ## Teria como por o comandante para respeitar o padrão VISA, mas o bagulho ta loco
        inst.close()
        porta_do_recurso = re.search('(COM\d*)',str(recurso))
        ser = serial.Serial(porta_do_recurso.group(0))
        ser.write(b'*IDN?')     # write a string
        identificador = [ser.readline()]
        ser.close()
        if(identificador[0]==b"CMDR!\n"):
            interface.box_controlador.addItem("Comandante (" + str(recurso) + ")")

def detect(interface,semafaro,running):
    import time
    import visa
    manager = visa.ResourceManager()
    while(True):
        semafaro.acquire()
        if running.is_set() is False:
            return
        interface.label_instrumento.setText("Atualizando...")
        #Limpa a lista de items
        for i in range(0,interface.box_instrumento.count()+1):
            interface.box_instrumento.removeItem(i)
        for i in range(0,interface.box_controlador.count()+1):
            interface.box_controlador.removeItem(i)
            
        resources = manager.list_resources()
        print(resources)       
        if len(resources) == 0:
            interface.box_instrumento.addItem("NADA DETECTADO")
            interface.box_instrumento.setCurrentIndex(1)
            interface.box_controlador.addItem("NADA DETECTADO")
            interface.box_controlador.setCurrentIndex(1)
        else:
            for resource in resources:
                identificar(manager,resource,interface)
            if interface.box_controlador.count() == 0:
                interface.box_controlador.addItem("NADA DETECTADO")
                interface.box_controlador.setCurrentIndex(1)
            if interface.box_instrumento.count() == 0:
                interface.box_instrumento.addItem("NADA DETECTADO")
                interface.box_instrumento.setCurrentIndex(1)
        interface.label_instrumento.setText("Atualizado.")
        time.sleep(1)