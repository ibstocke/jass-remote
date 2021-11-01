# HSLU
#
# Created by Thomas Koller on 7/28/2020
#
import logging
import numpy as np
from jass.agents.agent import Agent
from jass.game.const import PUSH, MAX_TRUMP, card_strings, color_masks
from jass.game.game_observation import GameObservation
from jass.game.rule_schieber import RuleSchieber
from jass.game.game_util import convert_one_hot_encoded_cards_to_int_encoded_list
from jass.game.game_util import convert_one_hot_encoded_cards_to_str_encoded_list
import jass.game.const as gc
import random

def prints():
    print("hello")

def havePuurWithFour(hand: np.ndarray) -> np.ndarray:
    result = np.zeros(4, dtype=int)

    for i in range(4):
        # check if color hase Jack
        if hand[gc.color_offset[i] + gc.J_offset]:
            # count number of cards of that color
            result[i] = hand[gc.color_offset[i]:gc.color_offset[i] + 9].sum() >= 4

    return result

class AgentBot001 (Agent):
    """
    Randomly select actions for the game of jass (Schieber)
    """
    def __init__(self):
        # log actions
        self._logger = logging.getLogger(__name__)
        # self._logger.setLevel(logging.INFO)
        # Use rule object to determine valid actions
        self._rule = RuleSchieber()
        # init random number generator
        self._rng = np.random.default_rng()



    def action_trump(self, obs: GameObservation) -> int:
        hand = obs.hand

        trump_color = 0
        trump_score = 0
        max_number_in_color = 0
        max_trump_score = 0

        obenabe_games = self._get_obenabe_games(hand)
        oneufe_games = self._get_oneufe_games(hand)
        obeabe_or_oneufe_games = max(oneufe_games, obenabe_games)

        for c in range(4):
            number_in_color = (hand * gc.color_masks[c]).sum()
            score = self._calculate_trump_selection_score(hand, c)
            if number_in_color > max_number_in_color:
                max_number_in_color = number_in_color
                trump_color = c
            if score > max_trump_score:
                max_trump_score = score
                trump_score = c

        # do de decision
        obe_une_score = obeabe_or_oneufe_games * 10
        do_trump_score = max_trump_score / np.sqrt(2)
        do_trump = False if obe_une_score > do_trump_score and obs.forehand == -1 else True

        if do_trump:
            have_puur_with4 = havePuurWithFour(obs.hand)
            puur_with4_color = -1
            if have_puur_with4.any() and max_trump_score >= 70:
                for j in range(4):
                    if have_puur_with4[j]:
                        return j

            if max_trump_score >= 68:
                return trump_score
            elif obs.forehand == -1:
                return gc.PUSH
            else:
                return trump_score
        else:
            if obenabe_games > oneufe_games:
                return gc.OBE_ABE
            else:
                return gc.UNE_UFE

    def action_play_card(self, obs: GameObservation) -> int:
        # cards are one hot encoded
        valid_cards = self._rule.get_valid_cards_from_obs(obs)

        if obs.nr_tricks <= 1 and obs.nr_cards_in_trick == 0 and obs.trump < gc.OBE_ABE:
            if valid_cards[obs.trump*9 + gc.J_offset]:
                return obs.trump*9 + gc.J_offset
            if obs.nr_tricks == 1:
                prev_trick = obs.tricks[0]
                force_to_play_trump = obs.trump * 9 <= prev_trick[(obs.player+1) % 4] < obs.trump * 9 + 9 and \
                                      obs.trump * 9 <= prev_trick[(obs.player+3) % 4] < obs.trump * 9 + 9

                if force_to_play_trump and valid_cards[obs.trump * 9 + gc.Nine_offset]:
                    return obs.trump * 9 + gc.Nine_offset

        # convert to list and draw a value
        self._do_monte_carlo(obs)
        card = self._rng.choice(np.flatnonzero(valid_cards))
        self._logger.debug('Played card: {}'.format(card_strings[card]))
        return card


    def _do_monte_carlo(self, obs : GameObservation):
        hand = self._rule.get_valid_cards_from_obs(obs)
        random_card = self._rng.choice(np.flatnonzero(hand))

        m = self.MonteCarloState(obs)


    def _calculate_trump_selection_score(self, hand, trump: int) -> int:
        card_list = convert_one_hot_encoded_cards_to_int_encoded_list(hand)
        trump_score = [15, 10, 7, 25, 6, 19, 5, 5, 5]
        no_trump_score = [9, 7, 5, 2, 1, 0, 0, 0, 0]

        score = 0
        for i in card_list:
            # check if card belongs to trump color
            if (gc.color_offset[trump] <= i < gc.color_offset[trump] + 9):
                score = score + trump_score[i % 9]
            else:
                score = score + no_trump_score[i % 9]
        return score


    def _get_obenabe_games(self, hand) -> int:
        count_of_games = self._get_number_of_save_games_obenabe(hand)
        sum_of_games = sum(count_of_games.values())

        best_color = max(count_of_games, key = count_of_games.get)
        if sum_of_games >=4 and count_of_games[best_color] >=3:
            number_of_cards_of_best_color = hand[best_color*9:best_color*9+9].sum()
            if number_of_cards_of_best_color >= 5:
                count_of_games[best_color] = number_of_cards_of_best_color
            elif number_of_cards_of_best_color >= 4:
                card_list = convert_one_hot_encoded_cards_to_int_encoded_list(hand[best_color * 9:best_color * 9 + 9])
                if max(card_list) <= 5:
                    count_of_games[best_color] = number_of_cards_of_best_color
        return sum(count_of_games.values())


    def _get_number_of_save_games_obenabe(self, hand) -> dict:
        count_of_games = {0: 0, 1: 0, 2: 0, 3: 0}
        for color in range(4):
            single_color = hand[color*9:color*9+9]
            for i in range(9):
                if single_color[i]:
                    count_of_games[color] += 1
                else:
                    break;
        return count_of_games

    def _get_oneufe_games(self, hand) -> int:
        count_of_games = self._get_number_of_save_games_oneufe(hand)
        sum_of_games = sum(count_of_games.values())

        best_color = max(count_of_games, key = count_of_games.get)
        if sum_of_games >=4 and count_of_games[best_color] >=3:
            number_of_cards_of_best_color = hand[best_color*9:best_color*9+9].sum()
            if number_of_cards_of_best_color >= 5:
                count_of_games[best_color] = number_of_cards_of_best_color
            elif number_of_cards_of_best_color >= 4:
                card_list = convert_one_hot_encoded_cards_to_int_encoded_list(hand[best_color * 9:best_color * 9 + 9])
                if min(card_list) >= 3:
                    count_of_games[best_color] = number_of_cards_of_best_color
        return sum(count_of_games.values())


    def _get_number_of_save_games_oneufe(self, hand) -> dict:
        count_of_games = {0: 0, 1: 0, 2: 0, 3: 0}
        for color in range(4):
            single_color = hand[color*9:color*9+9]
            for i in range(9):
                if single_color[i]:
                    count_of_games[color] += 1
                else:
                    break;
        return count_of_games

    class MonteCarloState:
        def __init__(self, obs : GameObservation):
            self._player_n = np.zeros(36)
            self._player_e = np.zeros(36)
            self._player_w = np.zeros(36)
            self._points = [0, 0]
            self._obs = obs
            self._init_cards()

        def _init_cards(self):
            myHand = self._obs.hand
            tricks = []
            for n in self._obs.tricks.flatten():
                if n >= 0:
                    tricks.append(n)
            played_cards = np.zeros(36)

            for i in range(36):
                for j in tricks:
                    if i == j:
                        played_cards[i] = 1
            remaining_cards = np.ones(36) - played_cards - myHand

            cards_per_player = np.floor(remaining_cards.sum() / 3)
            rest = remaining_cards.sum() % 3.0
            cards_for_player_n = cards_per_player
            cards_for_player_e = cards_per_player
            cards_for_player_w = cards_per_player

            if rest:
                rest -= 1
                cards_for_player_w += 1
            if rest:
                rest -= 1
                cards_for_player_n += 1

            next_player = 0
            for c in range(36):
                while remaining_cards[c]:
                    next_player = random.randint(0, 2)
                    if next_player == 0 and cards_for_player_e:
                        self._player_e[c] = 1
                        cards_for_player_e -= 1
                        remaining_cards[c] = 0
                    elif next_player == 1 and cards_for_player_n:
                        self._player_n[c] = 1
                        cards_for_player_n -= 1
                        remaining_cards[c] = 0
                    elif next_player == 2 and cards_for_player_w:
                        self._player_w[c] = 1
                        cards_for_player_w -= 1
                        remaining_cards[c] = 0