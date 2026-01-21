import serial
import time
import serial
from math import sin, cos, radians, pi, sqrt

debug = False

def mensagem(msg):
    if debug:
        print(msg)

class Carrinho:
    def __init__(self, modo='azimute'):
        #self._ser = serial.Serial('/dev/ttyACM0') # TODO: pode ser outra
        self._ser = serial.Serial('/dev/ttyUSB0') # TODO: pode ser outra
        mensagem('Aberta serial' + self._ser.name)
        time.sleep(2) # espera arduino resetar
        self.passos_mm = 40  # precisa calibrar!!!
        self.raio = 800  # precisa calibrar!!!
        self.azim = -90
        self.modo = modo
        try:
            assert modo in ['azimute','eleva']
        except AssertionError:
            print('Erro! `modo` deve ser "azimute" ou "eleva". Você falou', modo)
            import sys
            sys.exit(1)


    def r(self, azim):
        # referencial do experimento para radianos usuais
        return -(azim - 90) * pi / 180

    def __enter__(self):
        if self.modo == 'eleva':
            self.habilita_motores() 
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.modo == 'eleva':
            self.desabilita_motores()
        self._ser.close()

    def habilita_motores(self):
        mensagem("Habilitando motores")
        self._cmd('h')
        
    def desabilita_motores(self):
        mensagem("Desabilitanto motores")
        self._cmd('d')

    def anda_xy_mm(self, mm_x, mm_y):

        if self.modo == 'azimute':
            self.habilita_motores()

        dirx = self.direcao('x', mm_x)
        passosx = int(abs(mm_x) * self.passos_mm)

        diry = self.direcao('y', mm_y) 
        passosy = int(abs(mm_y) * self.passos_mm)

        mensagem(f'Vou dar {diry}{passosy} passos no eixo '
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

        xy = 'x' if eixo == 'pequeno' else 'y'

        dir = self.direcao(xy, mm)
        passos = int(abs(mm) * self.passos_mm)
        mensagem(f'Vou dar {dir}{passos} passos no eixo {eixo}')

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

    def anda_eleva_mirado(self, azim):
        return self.anda_azim_mirado(azim) 

    def anda_diagonal(self, dist):

        theta = self.r(self.azim)
        dgrande = dist * cos(theta)
        dpeq = dist * sin(theta)
        self.anda_xy_mm(dpeq, dgrande)

        self.raio += dist/abs(dist) * sqrt(dpeq**2 + dgrande**2)

        return dpeq*self.passos_mm, dgrande*self.passos_mm

    def anda_azim(self, azim):


        th0 = self.r(self.azim)
        th1 = self.r(azim)

        dgrande = self.raio * (cos(th1) - cos(th0))
        dpeq = self.raio * (sin(th1) - sin(th0))

        self.anda_xy_mm(dpeq, dgrande)

        self.azim = azim

        return dpeq*self.passos_mm, dgrande*self.passos_mm

    def direcao(self, eixo, passos):
        '''
        - Essa lógica depende de como estão conectados os motores de passo
        (direção em que foram espetados os conectores nos soquetes)
        - Depende também de como está montada a gaiola (se zero do azimute
        bate com zero da elevação)
        '''
        if  eixo in ('y','z') and self.modo == 'azimute':
            dir ='-' if passos > 0 else '+'
        else: 
            dir = '+' if passos > 0 else '-'

        return dir

    def anda_azim_mirado(self, azim):
        passos = int(1600 * (azim - self.azim) / 180)

        dir = self.direcao('z', passos)

        mensagem(f'vou andar {passos} para mirar a caixa')
        if self.modo == 'azimute':
            self.habilita_motores()
        self._cmd(f'pz{dir}{abs(passos)}')
        time.sleep(0.5) 
        if self.modo == 'azimute':
            self.desabilita_motores()
        return self.anda_azim(azim) 
        

    def sobe_mm(self, mm):
        passos = int(self.passos_mm * mm)
        mensagem(f'Vou dar {passos} passos')
        self.sobe(passos)

    def desce_mm(self, mm):
        passos = int(self.passos_mm * mm)
        mensagem(f'Vou dar {passos} passos')
        self.desce(passos)

    def delay(self, delay):
        mensagem(f'Ajustando delay para {delay} ms')
        self._cmd(f'c{delay}')

    def sobe(self, passos):
        self._cmd(f'p{passos}')

    def desce(self, passos):
        self._cmd(f'p-{passos}')

    def _cmd(self, arg):
        scmd = str(arg) + '\n'
        self._ser.write(scmd.encode("utf-8"))
