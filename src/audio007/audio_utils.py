import time
import sounddevice as sd
from scipy.io.wavfile import write, read
from scipy.signal import convolve
import numpy as np



def toca_audio(dados_wav, lado='ambos', taxa=None, filtro=None, ganho=1):
    if lado == 'ambos':
        lmap = [1,2]
    elif lado == 'esq':
        lmap = 1
    elif lado == 'dir':
        lmap = 2
    else:
        raise ValueError('O argumento `lado` deve ser: "esq", "dir" ou "ambos"(padrão)')

    # TODO: melhor fazer isso só uma vez, arquivos podem ser longos
    if isinstance(dados_wav, str): # le do arquivo
        taxa_wav, dados = read(dados_wav)
    else:
        taxa_wav = taxa #se for um array, tem que passar a taxa
        dados = dados_wav

    # TODO: isso fazia sentido para grilos, mas destrói a psicofísica!
    #if len(dados.shape) > 1:
    #    dados = dados.mean(axis=1).astype(dados.dtype)  # se for estéreo, mixa
    #    print('Áudio estéreo! Tomando média dos canais.')

    if taxa is None:
        taxa = taxa_wav
    else:
        taxa = 44100
   
    if filtro is not None:
        #filtro_e, filtro_d = filtro.T/32768
        #dados_e, dados_d = dados.T/32768

        #dados_e = convolve(dados_e, filtro_e, mode='full', method='auto')  
        #dados_d = convolve(dados_d, filtro_d, mode='full', method='auto')  
        #dados = np.c_[dados_e, dados_d]
        dados = dados / 32768  # TODO: conversão de int16 pra float hardcoded!
        filtro = filtro / 32768  # TODO: conversão de int16 pra float hardcoded!
        dados = np.c_[convolve(dados[:,0], filtro[:,0], mode='full', method='auto'),
                      convolve(dados[:,1], filtro[:,1], mode='full', method='auto')]

    sd.play(ganho*dados, mapping = lmap, blocking=True, samplerate=taxa)


def toca_grava(estimulo, saida):
    taxa_wav, est_array = read(estimulo)
    duracao = len(est_array)
    print(f'Começando a tocar {estimulo}. Duração:{duracao}s')
    print(f'Começando gravação')

    gravacao = sd.playrec(est_array, taxa_wav, channels=2, blocking=True)
    sd.wait()
    write(saida, taxa_wav, gravacao)

    print(f'Gravação concluída. Salvo arquivo {saida}.')


def grava_binaural(segundos, fname, fs = 44100): 

    if fname is None:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        fname = f'gravacao-{timestr}.wav'
    print(f'Começando gravação de {segundos}s')
    rec = sd.rec(int(segundos * fs), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    write(fname, fs, rec)
    print(f'Gravação concluída. Salvo arquivo {fname}.')

if __name__ == '__main__':
    print('gravando 5s em lixo.wav')
    grava_binaural(5, 'lixo.wav')
