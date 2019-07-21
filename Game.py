import pygame
import random
import time
import Qlearning


class Player:
    def __init__(self, sign):
        self.my_turn = False
        self.sign = sign

    @staticmethod
    def possible_moves(board):
        return [i for i in range(9) if not board[i]]


class HumanPlayer(Player):
    def move(self, board):
        event = self._wait_for_click()
        if event.type == pygame.QUIT:
            return "QUIT"
        pos = self._check_move_choice()
        if pos in Player.possible_moves(board):
            return pos
        return -1

    @staticmethod
    def _check_move_choice():
        (mouseX, mouseY) = pygame.mouse.get_pos()
        row, col = mouseY // (225 // 3), mouseX // (225 // 3)
        pos = row * 3 + col
        return pos

    @staticmethod
    def _wait_for_click():
        event = pygame.event.wait()
        while event.type != pygame.MOUSEBUTTONDOWN and event.type != pygame.QUIT:
            event = pygame.event.wait()
        return event


class CompPlayer(Player):
    def __init__(self, knowledge_filename, unjustified=0.1, *args, **kwargs):
        self.mind = Qlearning.Qlearning(MF=unjustified)
        self.knowledge_filename = knowledge_filename
        super(CompPlayer, self).__init__(*args, **kwargs)

    def move(self, board):
        return self.mind.choose_move(board, Player.possible_moves(board))

    def study(self, board, reward):
        self.mind.update_Qtable(board, Player.possible_moves(board), reward)

    def load_knowledge(self):
        self.mind.load_Qtable(self.knowledge_filename)

    def save_knowledge(self):
        self.mind.save_Qtable(self.knowledge_filename)


class TicTacToe:
    def __init__(self):
        self.board = ['']*9
        self.player1 = None
        self.player2 = None
        self.wsize = 225
        self.hsize = 250
        self.board_size = 225
        self.pause_time = 1
        self.surface = None
        self.ttt = None

    def play(self, *, with_comp=True):
        pygame.init()
        self._init_window()
        self._reset_game()
        self._show_board()
        self.player1 = HumanPlayer("X")
        if with_comp:
            self.player2 = CompPlayer(r"QlearnStats\secondPlayerMoves", unjustified=0, sign="O")
            self.player2.load_knowledge()
        else:
            self.player2 = HumanPlayer("O")
        order = [True, False]
        random.shuffle(order)
        self.player1.my_turn, self.player2.my_turn = order

        while True:
            pos = (self.player1.move(self.board) if self.player1.my_turn else self.player2.move(self.board))
            if pos == "QUIT":
                break
            if pos == -1:
                continue
            self._render(pos)
            reward = self._evaluate()
            if reward != 0:
                self._game_over(reward)
                if reward == 0.5:
                    random.shuffle(order)
                    self.player1.my_turn, self.player2.my_turn = order
            else:
                self.player1.my_turn, self.player2.my_turn = self.player2.my_turn, self.player1.my_turn

    def train(self, n_times=1_000_000):
        self.player1 = CompPlayer(r"QlearnStats\firstPlayerMoves", sign="X")
        self.player2 = CompPlayer(r"QlearnStats\secondPlayerMoves", sign="O")
        self.player1.load_knowledge()
        self.player2.load_knowledge()
        order = [True, False]
        random.shuffle(order)
        self.player1.my_turn, self.player2.my_turn = order

        for _ in range(n_times):
            pos = (self.player1.move(self.board) if self.player1.my_turn else self.player2.move(self.board))
            self._update_board(pos, self.player1.sign if self.player1.my_turn else self.player2.sign)
            reward = self._evaluate()
            if reward == 0:
                if self.player1.my_turn:
                    self.player2.study(self.board, reward)
                else:
                    self.player1.study(self.board, reward)
                self.player1.my_turn, self.player2.my_turn = self.player2.my_turn, self.player1.my_turn
            else:
                if reward == 1:
                    self.player1.study(self.board, (-1 if self.player2.my_turn else 1) * reward)
                    self.player2.study(self.board, (-1 if self.player1.my_turn else 1) * reward)
                else:
                    self.player1.study(self.board, reward)
                    self.player2.study(self.board, reward)
                    random.shuffle(order)
                    self.player1.my_turn, self.player2.my_turn = order
                self._update_board()

        self.player1.save_knowledge()
        self.player2.save_knowledge()

    def _init_window(self):
        self.ttt = pygame.display.set_mode((self.wsize, self.hsize))
        pygame.display.set_caption('Tic-Tac-Toe')

    def _render(self, move):
        sign = self.player1.sign if self.player1.my_turn else self.player2.sign
        self._update_board(move, sign)
        self._draw_move(move, sign)
        self._show_board()

    def _reset_game(self):
        self._update_board()
        self.surface = pygame.Surface(self.ttt.get_size()).convert()
        self.surface.fill((250, 250, 250))
        pygame.draw.line(self.surface, (0, 0, 0), (self.board_size//3, 0), (self.board_size//3, self.board_size), 2)
        pygame.draw.line(self.surface, (0, 0, 0), (self.board_size//1.5, 0), (self.board_size//1.5, self.board_size), 2)
        pygame.draw.line(self.surface, (0, 0, 0), (0, self.board_size//3), (self.board_size, self.board_size//3), 2)
        pygame.draw.line(self.surface, (0, 0, 0), (0, self.board_size//1.5), (self.board_size, self.board_size//1.5), 2)

    def _update_board(self, indices=range(9), sign=''):
        if isinstance(indices, int):
            self.board[indices] = sign
        else:
            for i in indices:
                self.board[i] = sign

    def _show_board(self):
        self.ttt.blit(self.surface, (0, 0))
        pygame.display.flip()

    def _draw_move(self, pos, sign):
        row = pos // 3
        col = pos % 3
        centerX = (col * self.board_size//3) + 32
        centerY = (row * self.board_size//3) + 32
        font = pygame.font.Font(None, 24)
        text = font.render(sign, 1, (10, 10, 10))
        self.surface.fill((250, 250, 250), (0, 300, 300, 25))
        self.surface.blit(text, (centerX, centerY))

    def _draw_reward(self, reward):
        msg = ("First player won!" if self.player1.my_turn else "Second player won!") if reward != 0.5 else "Draw!"
        font = pygame.font.Font(None, 24)
        text = font.render(msg, 1, (10, 10, 10))
        self.surface.fill((250, 250, 250), (0, 300, 300, 25))
        self.surface.blit(text, (10, 230))

    def _evaluate(self):
        for i in range(3):
            if self.board[i*3] == self.board[i*3+1] == self.board[i*3+2] and self.board[i*3]:
                return 1.0
            if self.board[i] == self.board[i+3] == self.board[i+6] and self.board[i]:
                return 1.0

        if self.board[4]:
            if self.board[0] == self.board[8] == self.board[4] or self.board[2] == self.board[4] == self.board[6]:
                return 1.0

        if all(self.board):
            return 0.5

        return 0.0

    def _game_over(self, reward):
        self._draw_reward(reward)
        self._show_board()
        time.sleep(self.pause_time)
        self._reset_game()
        self._show_board()


