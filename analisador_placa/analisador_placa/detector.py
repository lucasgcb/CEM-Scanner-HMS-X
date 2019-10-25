def detect(interface,semafaro,running):
    import time
    import visa
    manager = visa.ResourceManager()
    while(True):
        semafaro.acquire()
        if running.is_set() is False:
            return
        interface.label_instrumento.setText("Atualizando...")
        for i in range(0,interface.box_instrumento.count()+1):
            interface.box_instrumento.removeItem(i)
        resources = manager.list_resources()
        print(resources)       
        if len(resources) == 0:
            interface.box_instrumento.addItem("NADA DETECTADO")
            interface.box_instrumento.setCurrentIndex(1)
        else:
            for resource in resources:
                    interface.box_instrumento.addItem(resource)
            interface.box_instrumento.setCurrentIndex(1)
        interface.label_instrumento.setText("Atualizado.")
        time.sleep(1)