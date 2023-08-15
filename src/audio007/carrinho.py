import serial
import time
import serial
from math import sin, cos, radians, pi

class Carrinho:
    def __init__(self, modo='azimute'):
        #self._ser = serial.Serial('/dev/ttyACM0') # TODO: pode ser outra
        self._ser = serial.Serial('/dev/ttyUSB0') # TODO: pode ser outra
        print('Aberta serial', self._ser.name)
        time.sleep(2) # espera arduino resetar
        self.passos_mm = 40  # precisa calibrar!!!
        self.raio = 800  # precisa calibrar!!!
        self.azim = -90
        self.modo = modo

    def __enter__(self):
        if self.modo == 'eleva':
            self.habilita_motores() 
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.modo == 'eleva':
            self.desabilita_motores()
        self._ser.close()

    def habilita_motores(self):
        self._cmd('h')
        
    def desabilita_motores(self):
        self._cmd('d')

    def anda_xy_mm(self, mm_x, mm_y):

        if self.modo == 'azimute':
            self.habilita_motores()

        dirx = '+' if mm_x > 0 else '-'
        passosx = int(abs(mm_x) * self.passos_mm)

        diry = '+' if mm_y > 0 else '-'
        passosy = int(abs(mm_y) * self.passos_mm)

        print(f'Vou dar {diry}{passosy} passos no eixo '
                f'grande e {dirx}{passosx} no eixo pequeno')

        self._cmd(f'P{dirx}{passosx},{diry}{passosy}')

        if self.modo == 'azimute':
            self.desabilita_motores()

    def anda_mm(self, eixo, mm):
        if eixo not in ('grande', 'pequeno'):
            print("anda_mm recebe como primeiro parâmetro 'grande' ou 'pequeno'")
            return

        if self.modo == 'azimute':
            self.habilita_motores()

        dir = '+' if mm > 0 else '-'
        passos = int(abs(mm) * self.passos_mm)
        print(f'Vou dar {dir}{passos} passos no eixo {eixo}')

        xy = 'x' if eixo == 'pequeno' else 'y'
        self._cmd(f'p{xy}{dir}{passos}')

        if self.modo == 'azimute':
            self.desabilita_motores()

    def zera(self):
        self.desabilita_motores()
        input('Ponha manualmente na origem e aperte Enter...')
        self.azim = -90
        self.habilita_motores()
        self.anda_mm('grande', +70)
        if self.modo == 'azimute':
            self.desabilita_motores()
        
    def anda_eleva(self, eleva):
        self.anda_azim(eleva) 

    def anda_azim(self, azim):

        def r(azim):
            # referencial do experimento para radianos usuais
            return -(azim - 90) * pi / 180

        th0 = r(self.azim)
        th1 = r(azim)

        dgrande = self.raio * (cos(th1) - cos(th0))
        dpeq = self.raio * (sin(th1) - sin(th0))

        self.anda_xy_mm(dpeq, dgrande)

        self.azim = azim

        return dpeq*self.passos_mm, dgrande*self.passos_mm


    def sobe_mm(self, mm):
        passos = int(self.passos_mm * mm)
        print(f'Vou dar {passos} passos')
        self.sobe(passos)

    def desce_mm(self, mm):
        passos = int(self.passos_mm * mm)
        print(f'Vou dar {passos} passos')
        self.desce(passos)

    def delay(self, delay):
        print(f'Ajustando delay para {delay} ms')
        self._cmd(f'c{delay}')

    def sobe(self, passos):
        self._cmd(f'p{passos}')

    def desce(self, passos):
        self._cmd(f'p-{passos}')

    def _cmd(self, arg):
        scmd = str(arg) + '\n'
        self._ser.write(scmd.encode("utf-8"))
