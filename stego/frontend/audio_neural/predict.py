#!/usr/bin/env python3
# coding: utf-8

import logging as log
from audio_neural import model
from audio_neural import constants
from audio_neural import utils
import numpy as np
import tensorflow as tf
from pathlib import Path
import os

from audio_neural.text_to_spech import text_to_speech


class AudioNeural:
    def __init__(self):
        self.secret = '/app/stego/frontend/audio_neural/input_secret.wav'
        self.output_dir = os.path.join(constants.data_dir, 'predictions')
        self.secret_out = str(Path(self.output_dir) / Path('output_secret_input_secret.wav'))

    def encode(self, cover_path, text):
        text_to_speech(self.secret, text=text)
        self.secret_in = utils.convert_wav_to_stft_spec(self.secret)
        cover_in = utils.convert_wav_to_stft_spec(cover_path)
        if cover_in.shape[1] < self.secret_in.shape[1]:
            raise ValueError('Покрытие должно быть длиннее чем секретное')
        secret_in_begin = self.secret_in.shape[1]
        mdl = model.steg_model(cover_in.shape)
        mdl.load_weights('/app/stego/frontend/audio_neural/weight.hdf5')
        self.secret_in = utils.pad_single(self.secret_in, cover_in.shape[1] - self.secret_in.shape[1])
        secret_out, cover_out = mdl.predict(
            [np.array([self.secret_in]), np.array([cover_in])])

        secret_out = secret_out[:, :, :secret_in_begin, :]
        for output in [
            {
                'specgram': cover_out,
                'fname': 'output_cover_' + os.path.basename(cover_path) + '.wav'
            }, {
                'specgram': secret_out,
                'fname': 'output_secret_' + os.path.basename(self.secret)
            }
        ]:
            wav = utils.convert_stft_spec_to_wav(output['specgram'][0])
            full_fname = os.path.join(self.output_dir, output['fname'])
            tf.io.write_file(full_fname, wav, name=None)
            log.info('Spectrogram converted to wav: {}'.format(full_fname))
        return os.path.join(self.output_dir, 'output_cover_' + os.path.basename(cover_path)) + '.wav'
    
    def decode(self):
        return self.secret_out