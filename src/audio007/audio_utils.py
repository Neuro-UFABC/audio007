import time
import sounddevice as sd
from scipy.io.wavfile import write, read
from scipy.signal import convolve
import numpy as np
import pyloudnorm as pyln

sd.default.latency = [0.1, 0.1]


def toca_audio(dados_wav, lado='ambos', taxa=None, filtro=None, ganho=[1,1], tipo='int16'):
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
   

    ## ATENÇÃO: CONVERSÃO PARA FLOAT HARDCODED
    if tipo == 'int16':
        dados = dados / 2**15  
    elif tipo == 'int32':
        dados = dados / 2**31  
    else:
        print('Tipo desconhecido!! Abortando...')
        return 1

    if filtro is not None:
        dados = filtra(dados, filtro)

    sd.play(ganho*dados, mapping = lmap, blocking=True, samplerate=taxa)



def toca_grava(estimulo, saida, ganho=[1,1]):
    taxa_wav, est_array = read(estimulo)
    est_array *= ganho
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

##############################
# Refatorando

def nivel(som, taxa=None):
    if type(som) == str:
        rate, data = read(som)
    else:
        data = som
        rate = taxa
    meter = pyln.Meter(rate)
    return meter.integrated_loudness(data)


def ganho_normalizador(estimulo, referencia, taxa=None):
    delta = nivel(referencia, taxa) - nivel(estimulo, taxa)
    return np.power(10.0, delta/20.0)


def wavfile_pra_array(filename):
    taxa, dados = read(filename)

    if np.issubdtype(dados.dtype, np.integer):
        print(f'Convertendo wav de {dados.dtype} para float!')
        dmax = np.iinfo(dados.dtype).max
        dados = dados.astype(np.float32) / dmax

    return taxa, dados

def centra_normaliza(dados):
    #print('Centralizando cada canal (não muda ILD!)')
    dados = dados - np.mean(dados, axis=0, keepdims=True)

    dado_max = np.abs(dados).max() 
    if dado_max > 1:
        print(f'Normalizando dados, máximo absoluto {dado_max : .3f} > 1!')
        dados /= dado_max 

    return dados

def filtra(dados, filtro):
    return np.c_[convolve(dados[:,0], filtro[:,0], mode='full', method='auto'),
                      convolve(dados[:,1], filtro[:,1], mode='full', method='auto')]


def _tocagrava(entrada, saida, filtro=None, ganho=[1,1]):
    taxa_entrada, est_array = wavfile_pra_array(entrada)

    if filtro:
        taxa_filtro, filtro_array = wavfile_pra_array(filtro)
        if taxa_filtro != taxa_entrada:
            print('Taxa de amostragem da entrada diferente da do filtro! Desisto!!')
            return 1
        #print(filtro_array)
        est_array = filtra(est_array, filtro_array)

    est_array *= ganho
    est_array = centra_normaliza(est_array) 

    duracao = len(est_array)
    print(f'Começando a tocar {entrada}. Duração:{duracao/taxa_entrada : .3f}s')
    print(f'Começando gravação')

    gravacao = sd.playrec(est_array, taxa_entrada, channels=2, blocking=True, dtype='float32')
    sd.wait()
    write(saida, taxa_entrada, gravacao)



def _grava_binaural(segundos, fname, fs = 44100): 

    if fname is None:
        timestr = time.strftime("%Y%m%d-%H%M%S")
        fname = f'gravacao-{timestr}.wav'
    print(f'Começando a tocar {entrada}. Duração:{segundos/fs: .3f}s')
    rec = sd.rec(int(segundos * fs), samplerate=fs, channels=2, format='float32')
    sd.wait() 
    write(fname, fs, rec)
    print(f'Gravação concluída. Salvo arquivo {fname}.')

def _toca(dados_wav, lado='ambos', taxa=None, filtro=None, ganho=[1,1]):
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
        taxa_wav, est_array = read(dados_wav)
    else:
        taxa_wav = taxa #se for um array, tem que passar a taxa
        est_array = dados_wav

    # TODO: isso fazia sentido para grilos, mas destrói a psicofísica!
    #if len(dados.shape) > 1:
    #    dados = dados.mean(axis=1).astype(dados.dtype)  # se for estéreo, mixa
    #    print('Áudio estéreo! Tomando média dos canais.')

    if taxa is None:
        taxa = taxa_wav
    else:
        taxa = 44100
   
    if filtro:
        taxa_filtro, filtro_array = wavfile_pra_array(filtro)
        if taxa_filtro != taxa:
            print('Taxa de amostragem da entrada diferente da do filtro! Desisto!!')
            return 1
        #print(filtro_array)
        est_array = filtra(est_array, filtro_array)

    est_array *= ganho
    est_array = centra_normaliza(est_array) 

    duracao = len(est_array)
    print(f'Começando a tocar {dados_wav}. Duração:{duracao/taxa : .3f}s')

    gravacao = sd.playrec(est_array, taxa, channels=2, blocking=True, dtype='float32')
    sd.wait()



if __name__ == '__main__':
    print('gravando 5s em lixo.wav')
    grava_binaural(5, 'lixo.wav')
