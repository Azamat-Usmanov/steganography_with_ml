import numpy as np
from scipy.io import wavfile
import logging


SYM_LEN_IN_BITS = 11  # To support cyrillic letters from 'А' to 'я'
FREQ_TO_START = 2
NU_ADDITION = 1
TOL = 1

class AudioPhase:
    def __init__(self):
        pass


    def string_to_bits(self, string):
        bits = ''
        for ch in string:
            trunc_bits = format(ord(ch), 'b')
            bits += '0'*(SYM_LEN_IN_BITS - len(trunc_bits)) + trunc_bits
        return bits


    def bits_to_string(self, bits):
        string = ''
        for i in range(len(bits)//SYM_LEN_IN_BITS):
            string += chr(int(bits[SYM_LEN_IN_BITS*i:SYM_LEN_IN_BITS*(i+1)], 2))
        return string


    def num_to_digits(self, num):
        str_num = str(num)
        digits = []
        for str_dig in str_num:
            digits.append(int(str_dig))
        return np.array(digits, dtype=np.int16)


    def fill_zeros(self, arr, final_len):
        arr = np.concatenate((arr, [0] * (final_len - len(arr))))
        return arr


    def get_fft_matrices(self, init_matr):
        rows = np.size(init_matr, 0); cols = np.size(init_matr, 1)
        fft_matr = np.zeros((rows, cols), dtype=np.complex128)
        amplitudes = np.zeros((rows, cols))
        phases = amplitudes.copy()
        delta_phases = phases.copy()
        fft_matr[0, :] = np.fft.fft(init_matr[0, :])
        amplitudes[0, :] = np.abs(fft_matr[0, :])
        phases[0, :] = np.angle(fft_matr[0, :])
        delta_phases[0, :] = np.zeros(cols)
        for i in range(1, rows):
            fft_matr[i, :] = np.fft.fft(init_matr[i, :])
            amplitudes[i, :] = np.abs(fft_matr[i, :])
            phases[i, :] = np.angle(fft_matr[i, :])
            delta_phases[i, :] = phases[i, :] - phases[i-1, :]
        return amplitudes, phases, delta_phases


    def get_new_phases(self, phases, delta_phases, secret_bits):
        N = np.size(phases, 0); K = np.size(phases, 1)
        tmp_phase = phases[0, : K//2 + 1]
        for i in range(len(secret_bits)):
            if secret_bits[i] == '0':
                tmp_phase[-(i+FREQ_TO_START)] = -np.pi/2
            elif secret_bits[i] == '1':
                tmp_phase[-(i+FREQ_TO_START)] = np.pi/2
        new_phases = np.zeros((N, K))
        new_phases[0, :] = np.concatenate((tmp_phase, -np.flip(tmp_phase[1:-(K%2+1)])))
        for i in range(1, N):
            new_phases[i, :] = new_phases[i-1, :] + delta_phases[i, :]
        return new_phases


    def build_steg_audio(self, amplitudes, new_phases):
        N = np.size(amplitudes, 0)
        K = np.size(amplitudes, 1)
        steg_samples = np.zeros((N, K), dtype=np.int16)
        for i in range(N):
            steg_samples[i, :] = np.real(np.fft.ifft(amplitudes[i, :] * np.exp(1j*new_phases[i, :])))
        return np.reshape(steg_samples, N*K)


    def encode(self, audio_container, secret):
        fs, samples = wavfile.read(audio_container)
        is_stereo = False
        if len(samples.shape) == 2:
            is_stereo = True
            samples_ch_2 = samples[:, 1]
            samples = samples[:, 0]
        secret_bits = self.string_to_bits(secret)
        K = np.int32(2 ** (np.ceil(np.log2(len(secret_bits)) + 1) + NU_ADDITION))
        assert K < len(samples)//2
        N = np.int32(np.ceil(len(samples) / K))
        samples = np.reshape(self.fill_zeros(samples, N*K), (N, K))
        amplitudes, phases, delta_phases = self.get_fft_matrices(samples)
        new_phases = self.get_new_phases(phases, delta_phases, secret_bits)
        K_arr = self.num_to_digits(K)
        steg_samples = np.concatenate((self.build_steg_audio(amplitudes, new_phases), [-1], K_arr), dtype=np.int16)
        if is_stereo:
            samples_ch_2 = self.fill_zeros(samples_ch_2, N*K + 1 + len(K_arr))
            steg_samples = np.stack((steg_samples, samples_ch_2), dtype=np.int16).T
        wavfile.write('steg_audio.wav', fs, steg_samples)
        return 'steg_audio.wav'


    def decode(self, audio_container):
        logging.info('test')
        _, steg_samples = wavfile.read(audio_container)
        logging.info(f'after read: {steg_samples=}')
        is_stereo = False

        if len(steg_samples.shape) == 2:
            steg_samples = steg_samples[:, 0]

        if steg_samples[-1] == -1: 
            return '<Не найдено зашифрованного сообщения>'
        
        logging.info('before for')
        K = 0
        for i in range(len(steg_samples)):
            logging.info(f'{K=}, {i=}, {steg_samples[-(i+1)]=}')
            if steg_samples[-(i+1)] == -1:
                break
            K += steg_samples[-(i+1)] * (10 ** i)

        logging.info('before fft')
        phases = np.angle(np.fft.fft(steg_samples[:K])[: K//2 + 1])
        logging.info(f'{phases.shape=}')
        secret_bits = ''
        for i in range(K//2 + 1):

            if np.abs(phases[-(i+FREQ_TO_START)] + np.pi/2) < TOL:
                secret_bits += '0'

            elif np.abs(phases[-(i+FREQ_TO_START)] - np.pi/2) < TOL:
                secret_bits += '1'

            else:
                break

        secret = self.bits_to_string(secret_bits)
        logging.info(f'{secret=}')
        return secret


if __name__ == '__main__':
    audiofile = 'audio.wav'

    audiophase = AudioPhase()
    audiophase.encode(audiofile, 'Защита информации ')
    secret = audiophase.decode('steg_audio.wav')
    print(secret)
    print(secret == 'Защита информации ')