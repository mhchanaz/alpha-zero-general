from collections import namedtuple
from skimage.util import view_as_windows
import numpy as np
import copy

DEFAULT_HEIGHT = 11
DEFAULT_WIDTH = 11

WinState = namedtuple('WinState', 'is_ended winner')

def find_pattern(array, pattern):
    pattern_rows, pattern_cols = pattern.shape

    # Pad the array to handle edge cases
    padded_array = np.pad(array, ((pattern_rows - 1, pattern_rows - 1), (pattern_cols - 1, pattern_cols - 1)), mode='constant')

    # Use view_as_windows to create sliding windows
    windows = view_as_windows(padded_array, pattern.shape)

    # Check for matches
    if np.isnan(pattern).any():
        mask = np.isnan(pattern)
        matches = np.logical_or(windows == pattern, mask).all(axis=(2, 3))
    else:
        matches = (windows == pattern).all(axis=(2, 3))

    if matches.any():
        return True
    else:
        return False

def filtermoves(input_matrix):
    if np.all(input_matrix == 0):
        # If the whole matrix is zero, return a mask with all True values
        return np.ones_like(input_matrix, dtype=bool)

    matrix = np.pad(input_matrix, 4, mode='wrap')
    rows, cols = matrix.shape
    combined_mask = np.zeros((rows, cols), dtype=bool)

    non_zero_indices = np.nonzero(matrix)
    non_zero_coords = list(zip(non_zero_indices[0], non_zero_indices[1]))

    for i, j in non_zero_coords:
        for di in range(-2, 3):
            for dj in range(-2, 3):
                if i + di >= 0 and i + di < rows and j + dj >= 0 and j + dj < cols:
                    if matrix[i + di, j + dj] == 0:
                        combined_mask[i + di, j + dj] = True

    # Remove the padding from the combined_mask
    combined_mask = combined_mask[4:rows-4, 4:cols-4]

    return combined_mask

class Board():
    """
    Connect4 Board.
    """

    def __init__(self, height=None, width=None, np_pieces=None): # DONE
        "Set up initial board configuration."
        self.height = height or DEFAULT_HEIGHT
        self.width = width or DEFAULT_WIDTH

        if np_pieces is None:
            self.np_pieces = np.zeros([self.height, self.width], dtype=np.int)
        else:
            self.np_pieces = np_pieces
            assert self.np_pieces.shape == (self.height, self.width)

    def add_stone(self, action, player):
        "Create copy of board containing new stone."
        y = action // self.width
        x = action % self.width
        if self.np_pieces[y][x] != 0:
            raise ValueError("Can't play %s on board %s" % (action, self))

        self.np_pieces[y][x] = player

    def get_valid_moves(self): 
        # Check for 0 in the entire array
        result = self.np_pieces == 0

        # Convert the result to a 1D binary array
        return result.flatten().astype(int)

    def get_filtered_moves(self): 
        # Check for 0 in the entire array
        result = filtermoves(self.np_pieces)

        # Convert the result to a 1D binary array
        return result.flatten().astype(int)

    def get_win_state(self):
        # Input: board = current configuration of the 11x11 matrix
        # Output: 1 or -1 to indicate which color wins; 2 if it is a draw; 0 if the game is not yet over
        #思路（可以增加new_added points input时）：（更简单，因为只用考虑当前增减的点的周围即可）
        #以增加的点为中心，能胜利的一定是增加棋子与上下左右斜着有可能会连成五个的；超过边界的可以用取余数来获取对应位置的棋子信息；
        #思路：
        #遍历所有点，每个点用dict记录，如果空就只引入key，如果有色就引入directions，依次遍历四个directions，途中经过的点会update到dict中，
        #没在dict里的就增加directions并删除当前direction（因为已经被现在遍历过了），在dict里的就删除当前direction即可；
        board = self.np_pieces
        board = board.T #board记录的矩阵信息与实际展示在棋盘上的信息是symmetric的，我们调整board，使得左上角是(0,0)，棋盘左下角对应board的(10,0)
        directions = [[0,1],[1,0],[1,1],[-1,1]]
        visited_nodes = {}
        blank_nodes = 0
        # print(board)
        for cur_color in [-1,1]: #依次寻找黑色棋子和白色棋子的联通性
            visited_nodes = {}
            for i in range(11):
                for j in range(11):
                    if board[i,j] == 0:
                        blank_nodes += 1 #记录空格子数
                        continue
                    if board[i,j] != cur_color:
                        continue
                    #将当前棋子更新到待遍历中
                    if (i,j) not in visited_nodes:
                        visited_nodes[(i,j)] = copy.deepcopy(directions)

                    #遍历所有directions看是否有连通棋子
                    for direction in copy.deepcopy(visited_nodes[(i,j)]): #注意这里for循环要用deepcopy！不然删除一次后就变了
                        #print('current directions',direction)
                        count_num = 0

                        cur_i,cur_j = i,j #在19*19棋盘上面的位置
                        cur_i_onboard,cur_j_onboard = i,j #在11*11棋盘上面的位置
                        #正向遍历
                        while board[cur_i_onboard,cur_j_onboard] == cur_color:
                            count_num += 1 #当前方向的棋子累积数加1

                            #更新到待遍历棋的记录中
                            if (cur_i_onboard,cur_j_onboard) not in visited_nodes:
                                visited_nodes[(cur_i_onboard,cur_j_onboard)] = copy.deepcopy(directions)
                            #删除当前结点的当前方向，正负没有关系，因为都是用一个direction来算正向和反向的信息；所以不用担心超出11*11棋盘时是否会变道
                            visited_nodes[(cur_i_onboard,cur_j_onboard)].remove(direction)



                            #计算下一个结点的位置
                            cur_i,cur_j = cur_i + direction[0],cur_j + direction[1]
                            cur_i_onboard,cur_j_onboard = cur_i%11,cur_j %11


                            #终止条件：一个方向的棋子数达到5个
                            if count_num == 5:

                                return WinState(True, cur_color)


                        #反向遍历:初始化时，注意当回溯到起始点时，直接回溯到起始点往反方向走一格的位置，避免同时对(i,j)处理两次；

                        cur_i,cur_j = i - direction[0] ,j - direction[1] #在19*19棋盘上面的位置
                        cur_i_onboard,cur_j_onboard = cur_i%11,cur_j %11 #在11*11棋盘上面的位置

                        while board[cur_i_onboard,cur_j_onboard] == cur_color:
                            count_num += 1#当前方向的棋子累积数加1
                           #更新待遍历棋子中
                            if (cur_i_onboard,cur_j_onboard) not in visited_nodes:
                                visited_nodes[(cur_i_onboard,cur_j_onboard)] = copy.deepcopy(directions)
                            #删除当前结点的当前方向，正负没有关系，因为都是用一个direction来算正向和反向的信息；所以不用担心超出11*11棋盘时是否会变道
                            #is_reverse = 0 if abs(cur_i-cur_i_onboard) + abs(cur_j-cur_j_onboard) == 0 else 1 #等于0表示没有在11*11棋盘外

                            visited_nodes[(cur_i_onboard,cur_j_onboard)].remove(direction)

                            #计算下一个结点的位置
                            cur_i,cur_j = cur_i - direction[0],cur_j - direction[1]
                            cur_i_onboard,cur_j_onboard = cur_i%11,cur_j %11

                            #终止条件：一个方向的棋子数达到5个
                            if count_num == 5:
                                return WinState(True, cur_color)

        if blank_nodes == 0: #当所有位置都被下完后，返回和局, Which is player 2's win
            return WinState(True, -0.01)


        return WinState(False, None)

    def get_danger_state(self, y, x, player, directions): # Note x and y are reversed because of np matrix, -player's turn
        board = np.pad(self.np_pieces, 4, mode='wrap')

        x = x + 4
        y = y + 4
        current = board[x][y]
        highest_priority = np.inf
        mult_threats = 0

        for direction in directions:

            sum = 1
            empty_end1 = False
            empty_end2 = False
            empty_middle = False
            empty_middle_pos = 0
            empty_middle_neg = 0
            empty_middle_sum = 0
            empty_middle_end1 = False
            empty_middle_end2 = False

            for i in range(1,5): # positive dir
                checking = board[x + i * direction[1]][y + i * direction[0]]
                if checking != current:
                    if checking == 0:
                        if empty_middle == False:
                            empty_middle = True
                            empty_end1 = True
                            continue
                        else:
                            empty_middle_end1 = True
                    break
                if empty_middle == True:
                    empty_middle_pos += 1
                    continue
                sum += 1
                

            empty_middle = False
            for i in range(1,5): # negative dir
                checking = board[x - i * direction[1]][y - i * direction[0]]
                if checking != current:
                    if checking == 0:
                        if empty_middle == False:
                            empty_middle = True
                            empty_end2 = True
                            continue
                        else:
                            empty_middle_end2 = True
                    break
                if empty_middle == True:
                    empty_middle_neg += 1
                    continue
                sum += 1

            empty_middle_sum = sum + max(empty_middle_pos, empty_middle_neg)

            if sum >= 5: # Wins
                priority = 1
                if highest_priority > priority: # Wins
                    highest_priority = priority
            
            if sum == 4 and empty_end1 and empty_end2: # Threats
                priority = 3
                if highest_priority > priority: # threats
                    highest_priority = priority

            if (sum == 3 and empty_end1 and empty_end2) or (sum == 4 and (empty_end1 ^ empty_end2)) or (empty_middle_sum == 3 and empty_middle_end1 and empty_middle_end2) or (empty_middle_sum >= 4): # single small threat
                mult_threats += 1

            if mult_threats >= 2: # double 3 or similar threats
                priority = 5
                if highest_priority > priority: # threats
                    highest_priority = priority

        return highest_priority

    def get_danger_state_backup(self, y, x, player, directions): # Note x and y are reversed because of np matrix, -player's turn
        board = np.pad(self.np_pieces, 4, mode='wrap')

        x = x + 4
        y = y + 4
        current = board[x][y]
        highest_priority = np.inf
        mult_threats = 0

        for direction in directions: # Check immediate wins

            sum = 1
            empty_end1 = False
            empty_end2 = False

            for i in range(1,5): # positive dir
                checking = board[x + i * direction[1]][y + i * direction[0]]
                if checking != current:
                    if checking == 0:
                        empty_end1 = True
                    break
                sum += 1
                

            empty_middle = False
            for i in range(1,5): # negative dir
                checking = board[x - i * direction[1]][y - i * direction[0]]
                if checking != current:
                    if checking == 0:
                        empty_end2 = True
                    break
                sum += 1

            if sum >= 5: # Wins
                priority = 1
                if highest_priority > priority: # Wins
                    highest_priority = priority
            
            if sum == 4 and empty_end1 and empty_end2: # Threats
                priority = 3
                if highest_priority > priority: # threats
                    highest_priority = priority

            if (sum == 3 and empty_end1 and empty_end2) or (sum == 4 and (empty_end1 ^ empty_end2)): # obvious double 3 or similar threats
                mult_threats += 1

            if mult_threats >= 2: # double 3 or similar threats
                priority = 5
                if highest_priority > priority: # threats
                    highest_priority = priority

        return highest_priority

    def get_setup_state(self):
        board = np.pad(self.np_pieces, 4, mode='wrap')

        templates = (
            np.array([[0, np.nan, np.nan, np.nan, np.nan],
                      [np.nan, 1, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan],
                      [np.nan, np.nan, np.nan, 1, np.nan],
                      [np.nan, np.nan, np.nan, np.nan, 0]]),
            np.array([[np.nan, np.nan, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, np.nan, np.nan, np.nan],
                      [0, 1, 1, 1, 0],
                      [np.nan, np.nan, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, np.nan, np.nan, np.nan]]),
            np.array([[np.nan, np.nan, np.nan, np.nan, 0],
                      [np.nan, np.nan, np.nan, 1, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan],
                      [np.nan, 1, np.nan, np.nan, np.nan],
                      [0, np.nan, np.nan, np.nan, np.nan]]),
            np.array([[np.nan, np.nan, 0, np.nan, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan],
                      [np.nan, np.nan, 0, np.nan, np.nan]]),
            np.array([[0, np.nan, np.nan, np.nan, np.nan, np.nan],
                      [np.nan, 1, np.nan, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, np.nan, 0, np.nan, np.nan],
                      [np.nan, np.nan, np.nan, np.nan, 1, np.nan],
                      [np.nan, np.nan, np.nan, np.nan, np.nan, 0]]),
            np.array([[0, np.nan, np.nan, np.nan, np.nan, np.nan],
                      [np.nan, 1, np.nan, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 0, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, np.nan, 1, np.nan, np.nan],
                      [np.nan, np.nan, np.nan, np.nan, 1, np.nan],
                      [np.nan, np.nan, np.nan, np.nan, np.nan, 0]]),
            np.array([[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
                      [0, 1, 1, 0, 1, 0],
                      [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]]),
            np.array([[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
                      [0, 1, 0, 1, 1, 0],
                      [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]]),
            np.array([[np.nan, np.nan, np.nan, np.nan, np.nan, 0],
                      [np.nan, np.nan, np.nan, np.nan, 1, np.nan],
                      [np.nan, np.nan, np.nan, 0, np.nan, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan, np.nan],
                      [np.nan, 1, np.nan, np.nan, np.nan, np.nan],
                      [0, np.nan, np.nan, np.nan, np.nan, np.nan]]),
            np.array([[np.nan, np.nan, np.nan, np.nan, np.nan, 0],
                      [np.nan, np.nan, np.nan, np.nan, 1, np.nan],
                      [np.nan, np.nan, np.nan, 1, np.nan, np.nan],
                      [np.nan, np.nan, 0, np.nan, np.nan, np.nan],
                      [np.nan, 1, np.nan, np.nan, np.nan, np.nan],
                      [0, np.nan, np.nan, np.nan, np.nan, np.nan]]),
            np.array([[np.nan, np.nan, 0, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 0, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 0, np.nan, np.nan, np.nan]]),
            np.array([[np.nan, np.nan, 0, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 0, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 1, np.nan, np.nan, np.nan],
                      [np.nan, np.nan, 0, np.nan, np.nan, np.nan]])
        )

        # Get the dimensions of the matrix and the template
        matrix_rows, matrix_cols = board.shape

        for template in templates:
            if find_pattern(board, template):
                return WinState(True, 1)

        templates = tuple(arr * -1 for arr in templates)

        for template in templates:
            if find_pattern(board, template):
                return WinState(True, -1)

        return WinState(False, None)

    def with_np_pieces(self, np_pieces):
        """Create copy of board with specified pieces."""
        if np_pieces is None:
            np_pieces = self.np_pieces
        return Board(self.height, self.width, np_pieces)

    def __str__(self):
        return str(self.np_pieces)