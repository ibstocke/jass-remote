from jass.predictors.card.p_card import PCard
from jass.game.game_observation import GameObservation
from jass.game.rule_schieber import RuleSchieber
from tensorflow import keras
import numpy as np


class PNeuronalCard(PCard):

    def __init__(self):
        self._rule = RuleSchieber()
        self._model = keras.models.load_model('jass/predictors/card/play_card.h5')
        self._rng = np.random.default_rng()

    def action_play_card(self, obs: GameObservation) -> int:
        valid_cards = self._rule.get_valid_cards_from_obs(obs)

        features = self.obs_to_single_list(obs)
        prediction = self._model.predict(features)
        best_choice = np.squeeze(np.argsort(prediction))[::-1]
        for idx in best_choice:
            if valid_cards[idx] == 1:
                return idx

        return self._rng.choice(np.flatnonzero(valid_cards))

    def obs_to_single_list(self, obs: GameObservation) -> list:
        trump = np.zeros(6, dtype=int)
        trump[obs.trump] = 1

        played_tricks_arr = np.zeros(36, dtype=int)
        current_trick = np.zeros(108, dtype=int)
        tricks = obs.tricks
        for trick in tricks:
            if trick[3] != -1:
                played_tricks_arr[trick] = 1
            else:
                for player_idx, card in enumerate(trick):
                    if card == -1:
                        break
                    card_one_hot = np.zeros(36, dtype=int)
                    card_one_hot[card] = 1
                    start_idx = player_idx * 36
                    current_trick[start_idx:start_idx + 36] = card_one_hot

        return_list = trump
        return_list = np.append(return_list, obs.hand)
        return_list = np.append(return_list, played_tricks_arr)
        return_list = np.append(return_list, current_trick)
        return return_list.reshape(1, -1)
