import time
import sounddevice as sd
from scipy.io.wavfile import write, read



def toca_audio(arquivo_wav, lado='ambos', taxa=None):
    if lado == 'ambos':
        lmap = [1,2]
    elif lado == 'esq':
        lmap = 1
    elif lado == 'dir':
        lmap = 2
    else:
        raise ValueError('O argumento `lado` deve ser: "esq", "dir" ou "ambos"(padrão)')

    # TODO: melhor fazer isso só uma vez, arquivos podem ser longos
    taxa_wav, dados = read(arquivo_wav)

    if len(dados.shape) > 1:
        dados = dados.mean(axis=1).astype(dados.dtype)  # se for estéreo, mixa
        print('Áudio estéreo! Tomando média dos canais.')

    if taxa is None:
        taxa = taxa_wav
    else:
        taxa = 44100

    sd.play(dados, mapping = lmap, blocking=True, samplerate=taxa)

def toca_grava(estimulo, saida):
    taxa_wav, est_array = read(estimulo)
    duracao = len(est_array)
    print(f'Começando a tocar {estimulo}. Duração:{duracao}s')
    print(f'Começando gravação')

    gravacao = sd.playrec(est_array, taxa_wav, channels=2, blocking=True)
    sd.wait()
    write(saida, taxa_wav, gravacao)

    print(f'Gravação concluída. Salvo arquivo {saida}.')


def grava_binaural(segundos, fname):
    fs = 44100  # Sample rate

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
