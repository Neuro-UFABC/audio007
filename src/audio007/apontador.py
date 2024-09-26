import serial
import time
import serial
from scipy.interpolate import interp1d

class Apontador:
    def __init__(self, modo='eleva'):
        self._ser = serial.Serial('/dev/ttyACM0') 
        #self._ser = serial.Serial('/dev/ttyUSB0') # TODO: pode ser outra
        print('Aberta serial', self._ser.name)
        time.sleep(2) # espera arduino resetar

        print('Usando calibração tosca!! lembre-se de calibrar!!')
        self.pot_min = 770
        self.pot_max = 173


        # TODO: isso precisa ser medido!
        self.angulo_max = 90
        self.angulo_min = -90
    
        self.modo = modo

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._ser.close()

    def le_pot_motor(self):
        ret = self._cmd('m')
        val = int(ret)
        return val
    
    def le_pot_linear(self):
        ret = self._cmd('l')
        val = int(ret)
        return val

    def anda(self, passos):
        dir = '' if passos > 0 else '-'
        self._cmd(f'p{dir}{abs(passos)}')
    
    def sobe(self, passos):
        self._cmd(f'p{passos}')

    def desce(self, passos):
        self._cmd(f'p-{passos}')

    def botao_apertado(self):
        bot = int(self._cmd('b'))
        return bool(bot)

    def espera_botao(self):
        bot = self._cmd('b')
        t_aperta = 0
        while t_aperta < 5:
            if self._cmd('b') != bot:
                t_aperta += 1
            else:
                t_aperta = 0
            time.sleep(0.001)
    
    def quantos_graus(self):
        interp = interp1d([self.pot_min, self.pot_max],
                [self.angulo_min, self.angulo_max],
                fill_value='extrapolate')
        ang = interp(self.le_pot_motor()).tolist() 
        return ang

    def distancia(self):
        interp = interp1d([self.pot_linear_min, self.pot_linear_max],
                [0, 1],
                fill_value='extrapolate')
        dist = interp(self.le_pot_linear()).tolist() 
        return dist

    def calibra_linear(self):
        print('Aponte para longe.')
        print('Depois, aperte o botão')
        self.espera_botao()
        self.pot_linear_max = self.le_pot_linear()

        self.espera_botao()
        print('Aponte para perto.')
        print('Depois, aperte o botão')
        self.espera_botao()
        self.pot_linear_min = self.le_pot_linear()

        return self.pot_linear_min, self.pot_linear_max

    def calibra(self):
        if self.modo == 'azimute':
            print('Aponte para o máximo da direita.')
        else:
            print('Aponte para o máximo do alto.')
        print('Depois, aperte o botão')
        self.espera_botao()
        self.pot_max = self.le_pot_motor()

        self.espera_botao()
        if self.modo == 'azimute':
            print('Aponte para o máximo da esquerda.')
        else:
            print('Aponte para o máximo do baixo.')
        print('Depois, aperte o botão')
        self.espera_botao()
        self.pot_min = self.le_pot_motor()

        return self.pot_min, self.pot_max

    def habilita_motor(self):
        self._cmd('h')

    def desabilita_motor(self):
        self._cmd('d')

    def _cmd(self, arg):
        scmd = str(arg) + '\n'
        self._ser.write(scmd.encode("utf-8"))
        return self._ser.readline().strip()
