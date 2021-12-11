
from jass.game.game_observation import GameObservation


class PCard:
    def action_play_card(self, obs: GameObservation) -> int:
        """
        Agent to act as a player in a game of jass.
        """
        raise NotImplementedError