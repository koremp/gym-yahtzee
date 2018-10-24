from random import Random
from typing import Dict, Optional, Set

from gym_yahtzee.component import (
    action_to_scorebox_map,
    action_to_dice_roll_map,
    ScoreBox,
    SCOREBOX_ACTION_OFFSET,
    scorebox_to_action_map,
    scorebox_to_scoring_function_map,
)
from gym_yahtzee.scoring import score_upper_section_bonus

class State:
    def __init__(self, seed: int = None):
        self.upper_section_score = 0
        self.turn = 0
        self.dice = [0, 0, 0, 0, 0]
        self.scores: Dict[ScoreBox, Optional[int]] = {}

        if seed:
            self.rnd = Random(seed)
        else:
            self.rnd = Random()
        self.roll_dice(True, True, True, True, True)

    def roll_dice(self, d1: bool, d2: bool, d3: bool, d4: bool, d5: bool):
        dice = [d1, d2, d3, d4, d5]
        for i, die in enumerate(dice):
            if die:
                self.dice[i] = self.rnd.choice([1, 2, 3, 4, 5, 6])

    def get_possible_actions(self):
        possible_actions = []

        # determine if rerolling dice is possible; is so, add all possible permutations
        if self.turn < 3:
            possible_actions.extend(list(range(31)))

        # See which scoreboxex are still unused
        for scorebox in ScoreBox:
            if not self.scores.get(scorebox):
                action = scorebox_to_action_map.get(scorebox)
                # Check if the scorebox has an action associated with it
                # (upper section bonus is automatic).
                if action:
                    possible_actions.append(action)

        return possible_actions

    def take_action(self, action: int) -> int:
        possible_actions = self.get_possible_actions()
        if action not in possible_actions:
            return 0

        # if dice rolling action
        if action < SCOREBOX_ACTION_OFFSET:
            self.turn += 1
            self.roll_dice(*action_to_dice_roll_map[action])
            return 0

        scorebox = action_to_scorebox_map[action]
        scoring_function = scorebox_to_scoring_function_map[scorebox]
        reward = scoring_function(self.dice)
        self.scores[scorebox] = reward

        # upper section
        if SCOREBOX_ACTION_OFFSET <= action <= SCOREBOX_ACTION_OFFSET + 5:
            self.upper_section_score += reward
            upper_scores = [v for k, v in self.scores.items()
                            if int(k) <= int(ScoreBox.SIXES)]
            if len(upper_scores) == 6:
                bonus_reward = score_upper_section_bonus(self.upper_section_score)
                self.scores[ScoreBox.UPPER_SECTION_BONUS] = bonus_reward
                reward += bonus_reward

        return reward
