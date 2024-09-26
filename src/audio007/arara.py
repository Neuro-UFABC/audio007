import serial
import time


class Arara:
    def __init__(self, modo='eleva'):
        #self._ser = serial.Serial('/dev/ttyACM0') # TODO: pode ser outra
        self._ser = serial.Serial('/dev/ttyUSB0') # TODO: pode ser outra
        print('Aberta serial', self._ser.name)
        time.sleep(2) # espera arduino resetar

    def __exit__(self, exc_type, exc_value, traceback):
        self._ser.close()
    
    def habilita_caixa(self, qual):
        self._cmd(int(qual))

    def desabilita_caixas(self):
        self._cmd(0)

    def _cmd(self, arg):
        scmd = str(arg) 
        self._ser.write(scmd.encode("utf-8"))
        
    def angulo_falante(self, falante):
        # TODO: logica para azim/eleva
        return -90 + 30 * (falante - 1)
