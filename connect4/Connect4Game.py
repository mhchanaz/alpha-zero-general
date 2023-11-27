import sys
import numpy as np

sys.path.append('..')
from Game import Game
from .Connect4Logic import Board

directions = ([0,1],[1,0],[1,1],[-1,1])

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

    def SgetNextState(self, board, player, action): # Used in getting smart moves only
        b = self._base_board.with_np_pieces(np_pieces=np.copy(board))
        b.add_stone(action, player)
        return b.np_pieces, player, action

    def getValidMoves(self, board, player):
        "Any zero value in top row in a valid move"
        return self._base_board.with_np_pieces(np_pieces=board).get_valid_moves()

    def getDanger(self, board, player, action):

        y = action // 11
        x = action % 11
        b = self._base_board.with_np_pieces(np_pieces=board)

        return b.get_danger_state(x, y, player, directions) # Action played and now its -player's turn, proceed the checks

    """
    def getSetup(self, board, player):
        b = self._base_board.with_np_pieces(np_pieces=board)
        winstate = b.get_setup_state()
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
    """

    def getSmartMoves(self, board, player):
        "Any zero value in top row in a valid move"
        valid_moves = self._base_board.with_np_pieces(np_pieces=board).get_filtered_moves() # Filters out all the values outside 2 elements of existing

        if np.all(self._base_board.with_np_pieces(np_pieces=board).np_pieces == 0): # first step
            win_move_set = np.full(len(valid_moves), 0)  # Initialize all elements to 0
            win_move_set[np.random.randint(0, 120)] = 1  # Set the specified index to 1
            return win_move_set

        move_set = None
        highest_priority = 10

        for move, valid in enumerate(valid_moves): # One step away from win or losing, if none of the above applies
            if not valid: continue
            priority = self.getDanger(*self.SgetNextState(board, player, move))

            if (priority) and (priority <= highest_priority): # 0 is highest priority
                if priority < highest_priority:
                    move_set = np.full(len(valid_moves), 0)
                move_set[move] = 1  # Set the specified index to 1
                highest_priority = priority

            priority = self.getDanger(*self.SgetNextState(board, -player, move))
            priority += 1

            if (priority) and (priority <= highest_priority): # 0 is highest priority
                if priority < highest_priority:
                    move_set = np.full(len(valid_moves), 0)
                move_set[move] = 1  # Set the specified index to 1
                highest_priority = priority
        
        if move_set is None:
            return valid_moves

        return move_set

        # The following section is too greedy.
        '''
        setup_move_set = [0] * len(valid_moves)
        have_setup = False

        for move, valid in enumerate(valid_moves): # One step away from a setup from winning or losing, return all possibilities instead of breaking
            if not valid: continue
            if -player == self.getSetup(*self.getNextState(board, player, move)):
                setup_move_set[move] = 1
                have_setup = True
            if -player == self.getSetup(*self.getNextState(board, -player, move)):
                setup_move_set[move] = 1
                have_setup = True
        
        if have_setup:
            return setup_move_set
        else:
            return valid_moves # No setups found
        '''

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