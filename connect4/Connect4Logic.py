from collections import namedtuple
import numpy as np
import copy

DEFAULT_HEIGHT = 11
DEFAULT_WIDTH = 11

WinState = namedtuple('WinState', 'is_ended winner')


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
            return WinState(True, -1)


        return WinState(False, None)

    def with_np_pieces(self, np_pieces):
        """Create copy of board with specified pieces."""
        if np_pieces is None:
            np_pieces = self.np_pieces
        return Board(self.height, self.width, np_pieces)

    def __str__(self):
        return str(self.np_pieces)