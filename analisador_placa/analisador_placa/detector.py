import time

def detect(interface,semafaro):
    import visa
    manager = visa.ResourceManager()
    while(True):
        semafaro.acquire()
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
        time.sleep(1)