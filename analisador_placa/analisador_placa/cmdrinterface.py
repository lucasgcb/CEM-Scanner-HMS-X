import os
import serial
import time
import warnings
class Commander:
    """
    Interface do MCC
    A fazer:
    Não travar a thread enquanto espera leitura.
    """
    def __init__(self, resource_name):
        self.interface = serial.Serial(resource_name)
        self.query('*IDN?')
        id_instrument = self.query('*IDN?')  
        if id_instrument == "CMDR!\n":
            connect_attempt = self.query('*CONN') 
        else:
            raise Exception

    def connect(self):
        return self.query("*CONN")

    def disconnect(self):
        return self.query("*DISC")

    def close(self):
        self.query("*DISC")
        self.interface.close()
    def set_stepY(self,val):
        return self.query("*SSTPY({})".format(int(val)))
    def set_stepX(self,val):
        return self.query("*SSTPX({})".format(int(val)))
    
    def move_X(self,val=+1,step=None):
        """
        Move X for the defined group of steps.
        Repeats the call for val.

        Parameters
        ----------
        val - Times to repeat
        """
        if step is not None:
            self.set_stepX(step)
        if val>=0:
            for _ in range(0,val):
                self.query("*MOVX+")
                self.interface.readline() ## Sempre responde MV#OK quando acaba
        else:
            for _ in range(0,val,-1):
                self.query("*MOVX-")
                self.interface.readline()

    def move_Y(self,val=+1,step=None):
        """
        Move X for the defined group of steps.
        Repeats the call for val.

        Parameters
        ----------
        val - Times to repeat
        step - New step, set to default step
        """
        
        if step is not None:
            self.set_stepY(step)

        if val>=0:
            for _ in range(0,val):
                self.query("*MOVY+")
                self.interface.readline()
        else:
            for _ in range(0,val,-1):
                self.query("*MOVY-")
                self.interface.readline()


    @property
    def stepX(self):
        return int(self.query('*STPX').split(',')[0])
    
    @property
    def stepY(self):
        return int(self.query('*STPY').split(',')[0])
    
    @property    
    def status(self):
        return self.query('*STAT')
    
            
    def query(self,comando):
        """
        comando -  Query String
        Makes an SCPI query, inquiring a response.
        """
        
        time.sleep(0.15) 
        try:
            self.interface.write("{}".format(comando).encode())
            resposta = self.interface.readline()
            return resposta.decode("utf-8") 
        except Exception as e:
            raise Exception
            
    @property           
    def hello(self):
        return 'Hello world, I am ' + self.query('*IDN?')
    
    @property  
    def identity(self):
        return self.query('*IDN?')
    
    