import visa
import os
import VISAresourceExtensions
import time
import warnings

class Instrument:
    def __init__(self, resource_name=None):
        self.manager = visa.ResourceManager()
        if resource_name is None:
            ## If none provided, get the
            ## First  resource on the list
            
            id_instrument = self.manager.list_resources()[0]
        else:
            id_instrument = resource_name
            
        self.interface = self.manager.open_resource(id_instrument)
        self.interface.write_termination = '\n'
        self.interface.ext_clear_status()  # Clear instrument io buffers and status
        self.write('*RST;*CLS')  # Reset the instrument, clear the Error queue
        self.write('INIT:CONT ON')  # Switch OFF the continuous sweep
        self.write('SYST:DISP:UPD OFF')  # Display update ON - switch OFF after debugging
    
    def close(self):
        self.interface.close()
        
    def activate_mode_receiver(self):
        self.write('SYST:MODE RMOD')
    
    @property
    def receiver_step(self):
        return float(self.query('RMOD:FREQ:STEP?'))
    
    @property
    def receiver_frequency(self):
        return float(self.query('RMODe:LEV?').split(',')[0])
    
    @property    
    def receiver_level(self):
        return float(self.query('RMODe:LEV?').split(',')[1])
    
    def receiver_set_step(self, freq):
        self.write('RMOD:FREQ:STEP {}'.format(freq))
    
    def activate_mode_sweep(self):
        self.write('SYST:MODE SWE')
        
    def write(self,comando):
        """
        comando -  Command String
        Sends a command based on SCPI.
        """
        
        time.sleep(0.5) 
        try:
            self.interface.write(comando)
        except Exception as e:
            raise Exception
            
    def query(self,comando):
        """
        comando -  Query String
        Makes an SCPI query, inquiring a response.
        """
        
        time.sleep(0.5) 
        try:
            return self.interface.query(comando)
        except Exception as e:
            raise Exception
            
    @property           
    def hello(self):
        return 'Hello world, I am ' + self.query('*IDN?')
    
    @property   
    def identity(self, instrument):
        return self.interface.query('*IDN?')

    def screenshot(self, output_name):
        """
        output_name - string for output bmp filename.
        Take a screenshot.
        """
        time.sleep(2) 
        dir_atual = os.path.dirname(os.path.realpath(__file__))
        try:
            self.interface.ext_query_bin_data_to_file('HCOP:DATA?', dir_atual + "/{}.bmp".format(output_name))
            return 0
        except Exception as e:
            warnings.warn("Houve erro ao tirar screenshot:" + str(e), RuntimeWarning )

    
    