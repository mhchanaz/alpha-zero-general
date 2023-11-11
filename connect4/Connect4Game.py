import sys
import numpy as np

sys.path.append('..')
from Game import Game
from .Connect4Logic import Board


class Connect4Game(Game):
    """
    Connect4 Game class implementing the alpha-zero-general Game interface.
    """

    def __init__(self, height=None, width=None, np_pieces=None):
        Game.__init__(self)
        self._base_board = Board(height, width, np_pieces)

    def getInitBoard(self):
        return self._base_board.np_pieces

    def getBoardSize(self):
        return (self._base_board.height, self._base_board.width)

    def getActionSize(self):
        return self._base_board.width ** 2

    def getNextState(self, board, player, action):
        """Returns a copy of the board with updated move, original board is unmodified."""
        b = self._base_board.with_np_pieces(np_pieces=np.copy(board))
        b.add_stone(action, player)
        return b.np_pieces, -player

    def getValidMoves(self, board, player):
        "Any zero value in top row in a valid move"
        return self._base_board.with_np_pieces(np_pieces=board).get_valid_moves()

    def getGameEnded(self, board, player):
        b = self._base_board.with_np_pieces(np_pieces=board)
        winstate = b.get_win_state()
        if winstate.is_ended:
            if winstate.winner == player:
                return +1
            elif winstate.winner == -player:
                return -1
            elif winstate.winner == -0.01:
                return 0.01 * (player == -1) # Give less reward when winning via a draw
            else:
                raise ValueError('Unexpected winstate found: ', winstate)
        else:
            # 0 used to represent unfinished game.
            return 0

    def getCanonicalForm(self, board, player):
        # Flip player from 1 to -1
        return board * player

    def getSymmetries(self, board, pi):
        pi_board = np.reshape(pi, (11, 11))
        l = []
        l += [(board, list(pi_board.ravel()))]

        for i in range(1,11): # horizontal
            shifted_board = np.roll(board, i, axis=1)
            shifted_pi_board = np.roll(pi_board, i, axis=1)
            l += [(shifted_board, list(shifted_pi_board.ravel()))]
    
        for i in range(1,11): # vertical
            shifted_board = np.roll(board, i, axis=0)
            shifted_pi_board = np.roll(pi_board, i, axis=0)
            l += [(shifted_board, list(shifted_pi_board.ravel()))]
    
        newB = np.rot90(board, 1)
        newPi = np.rot90(pi_board, 1)

        for i in range(1,11): # horizontal
            shifted_board = np.roll(newB, i, axis=1)
            shifted_pi_board = np.roll(newPi, i, axis=1)
            l += [(shifted_board, list(shifted_pi_board.ravel()))]
    
        for i in range(1,11): # vertical
            shifted_board = np.roll(newB, i, axis=0)
            shifted_pi_board = np.roll(newPi, i, axis=0)
            l += [(shifted_board, list(shifted_pi_board.ravel()))]
    
        newB = np.rot90(board, 2)
        newPi = np.rot90(pi_board, 2)

        for i in range(1,11): # horizontal
            shifted_board = np.roll(newB, i, axis=1)
            shifted_pi_board = np.roll(newPi, i, axis=1)
            l += [(shifted_board, list(shifted_pi_board.ravel()))]
    
        for i in range(1,11): # vertical
            shifted_board = np.roll(newB, i, axis=0)
            shifted_pi_board = np.roll(newPi, i, axis=0)
            l += [(shifted_board, list(shifted_pi_board.ravel()))]

        newB = np.rot90(board, 3)
        newPi = np.rot90(pi_board, 3)

        for i in range(1,11): # horizontal
            shifted_board = np.roll(newB, i, axis=1)
            shifted_pi_board = np.roll(newPi, i, axis=1)
            l += [(shifted_board, list(shifted_pi_board.ravel()))]
    
        for i in range(1,11): # vertical
            shifted_board = np.roll(newB, i, axis=0)
            shifted_pi_board = np.roll(newPi, i, axis=0)
            l += [(shifted_board, list(shifted_pi_board.ravel()))]

        return l

    def stringRepresentation(self, board):
        return board.tostring()

    @staticmethod
    def display(board):
        print(" -----------------------")
        print(' '.join(map(str, range(len(board[0])))))
        print(board)
        print(" -----------------------")