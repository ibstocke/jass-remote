from jass.predictors.trump.p_trump import PTrump
import numpy as np
from tensorflow import keras
import os


class PTNEURONAL(PTrump):

    def __init__(self):
        self._modelWP: keras.Sequential = self._load_model_WP()
        self.modelFH: keras.Sequential = self._load_model_FH()

    @staticmethod
    def _load_model_WP():
        return keras.models.load_model('jass/predictors/trump/trump_wp.h5')

    @staticmethod
    def _load_model_FH():
        return keras.models.load_model('jass/predictors/trump/trump_fh.h5')

    def action_trump(self, hand: np.ndarray, forehand: bool) -> int:
        res = 0
        if forehand:
            res = self.modelFH.predict(hand.reshape(1, -1))
        else:
            res = self._modelWP.predict(hand.reshape(1, -1))

        res = np.argmax(res)
        if res == 6:
            # 6 and 10 indicate PUSH
            res = 10
        return res
