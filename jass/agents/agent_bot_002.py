
import numpy as np
from jass.agents.agent import Agent
from jass.game.game_observation import GameObservation
from jass.game.rule_schieber import RuleSchieber
import jass.game.const as gc

from jass.predictors.trump.neuronal import PTNEURONAL
from jass.predictors.card.neuronal import PNeuronalCard


class AgentBot002 (Agent):

    def __init__(self):
        self._rule = RuleSchieber()
        self._PT_neuronal = PTNEURONAL()
        self._PC_neuronal = PNeuronalCard()


    def action_trump(self, obs: GameObservation) -> int:

        is_forehand = obs.forehand == -1
        trump = self._PT_neuronal.action_trump(obs.hand, is_forehand)
        return trump


    def action_play_card(self, obs: GameObservation) -> int:
        # cards are one hot encoded
        valid_cards = self._rule.get_valid_cards_from_obs(obs)
        if valid_cards.sum() == 1:
            return np.argmax(valid_cards)

        if obs.nr_tricks <= 1 and obs.nr_cards_in_trick == 0 and obs.trump < gc.OBE_ABE:
            if valid_cards[obs.trump*9 + gc.J_offset]:
                return obs.trump*9 + gc.J_offset
            if obs.nr_tricks == 1:
                prev_trick = obs.tricks[0]
                force_to_play_trump = obs.trump * 9 <= prev_trick[(obs.player+1) % 4] < obs.trump * 9 + 9 and \
                                      obs.trump * 9 <= prev_trick[(obs.player+3) % 4] < obs.trump * 9 + 9

                if force_to_play_trump and valid_cards[obs.trump * 9 + gc.Nine_offset]:
                    return obs.trump * 9 + gc.Nine_offset

        card = self._PC_neuronal.action_play_card(obs)

        return card