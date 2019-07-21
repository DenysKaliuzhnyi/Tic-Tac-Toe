import random
import pickle
from collections import defaultdict


class Qlearning:
    def __init__(self, MF=0.1, LF=0.3, DF=0.3):
        self.MF = MF
        self.LF = LF
        self.DF = DF
        self.Q = defaultdict(lambda: 1.0)
        self.state_last = None
        self.move_last = None
        self.q_last = 0.0

    def choose_move(self, state, possible_moves):
        if random.random() < self.MF:
            move = random.choice(possible_moves)
        else:
            q_list = [self._getQ(tuple(state), move) for move in possible_moves]
            q_max = max(q_list)
            if q_list.count(q_max) > 1:
                best_options = [i for i in range(len(possible_moves)) if q_list[i] == q_max]
                best_i = random.choice(best_options)
            else:
                best_i = q_list.index(q_max)
            move = possible_moves[best_i]

        self.state_last = tuple(state)
        self.move_last = move
        self.q_last = self._getQ(self.state_last, move)
        return move

    def update_Qtable(self, state, possible_moves, reward):
        q_list = self._getQlist(state, possible_moves)
        q_max_new = (max(q_list) if q_list else 0.0)
        self._setQ(self.state_last,
                   self.move_last,
                   self.q_last + self.LF * ((reward + self.DF*q_max_new) - self.q_last))

    def _getQ(self, state, move):
        return self.Q[(state, move)]

    def _setQ(self, state, move, val):
        self.Q[(state, move)] = val

    def _getQlist(self, state, possible_moves):
        return [self._getQ(tuple(state), move) for move in possible_moves]

    def save_Qtable(self, file_name):
        with open(file_name, 'ab') as handle:
            pickle.dump(dict(self.Q), handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_Qtable(self, file_name):
        try:
            with open(file_name, 'rb') as handle:
                self.Q = defaultdict(lambda: 1.0, pickle.load(handle))
            print(self.Q)
        except EOFError:
            print(f"{file_name} is empty!")
