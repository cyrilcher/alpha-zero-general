import numpy as np
'''
Board class for the game of TicTacToe.
Default board size is 3x3.
Board data:
  1=white(O), -1=black(X), 0=empty
  first dim is column , 2nd is row:
     pieces[0][0] is the top left square,
     pieces[2][0] is the bottom left square,
Squares are stored and manipulated as (x,y) tuples.

Author: Evgeny Tyurin, github.com/evg-tyurin
Date: Jan 5, 2018.

Based on the board for the game of Othello by Eric P. Nichols.

'''
# from bkcharts.attributes import color
class Board():

    # list of all 8 directions on the board, as (x,y) offsets
    __directions = [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]

    def __init__(self, rows=6, cols=7, win=4):
        "Set up initial board configuration."

        self.rows = rows
        self.cols = cols
        self.win = win
        if rows < win:
            raise Exception('Incorrect win condition')
        if cols < rows:
            raise Exception('Invalid board configuration')
        # Create the empty board array.
        self.pieces = np.zeros((rows,cols))
        # self.pieces = [None]*self.cols
        # for i in range(self.cols):
        #     self.pieces[i] = [0]*self.rows

    # add [][] indexer syntax to the Board
    def __getitem__(self, index): 
        return self.pieces[index]

    def get_legal_moves(self, color):
        """Returns all the legal moves for the given color.
        (1 for white, -1 for black)
        @param color not used and came from previous version.        
        """
        moves = set()  # stores the legal moves.

        # Get all the empty squares (color==0)
        for col in range(self.cols):
            for row in reversed(range(self.rows)):
                if self[row][col]==0:
                    newmove = (row,col)
                    moves.add(newmove)
                    break
        return list(moves)

    def has_legal_moves(self):
        for col in range(self.cols):
            if self[0][col]==0:
                return True
        return False
    
    def check_line(self, line, color):

        extended_line = np.concatenate([line, line[:self.win-1]])

        for i in range(len(line)):
            if all([extended_line[i] == extended_line[i + j] != 0 for j in range(self.win)]):
                return extended_line[i] == color
        return False
    
    def is_win(self, color):
        """Check whether the given player has collected a triplet in any direction; 
        @param color (1=white,-1=black)
        """
        # check y-strips
        for col in range(self.cols):
            if self.check_line(self[:, col], color):
                return True
        # check x-strips
        for row in range(self.rows):
            if self.check_line(self[row, :], color):
                return True
        # for 6x7 board
        # check diagonal strips
        full_diag = []
        for col in range(self.cols):
            full_diag.append(np.concatenate([np.diagonal(self.pieces, offset=col), np.diagonal(self.pieces, offset=col - self.cols)]))
        full_diag = np.concatenate([full_diag[0]] + full_diag[1:][::-1])
        if self.check_line(full_diag, color):
            return True
        # check other diagonal strips
        full_diag = []
        for col in range(self.cols):
            full_diag.append(np.concatenate([np.diagonal(np.flip(self.pieces, 0), offset=col), np.diagonal(np.flip(self.pieces, 0), offset=col - self.cols)]))
        full_diag = np.concatenate([full_diag[0]] + full_diag[1:][::-1])
        if self.check_line(full_diag, color):
            return True
        # # if board is square
        # # check diagonal strips
        # for col in range(self.cols):
        #     diag_line = np.concatenate([np.diagonal(self.pieces, offset=col), np.diagonal(self.pieces, offset=col - self.cols)])
        #     if self.check_line(diag_line, color):
        #         return True
        # # check other diagonal strips
        # for col in range(self.cols):
        #     diag_line = np.concatenate([np.diagonal(np.flip(self.pieces, 0), offset=col), np.diagonal(np.flip(self.pieces, 0), offset=col - self.cols)])
        #     if self.check_line(diag_line, color):
        #         return True
            
        return False

    def execute_move(self, move, color):
        """Perform the given move on the board; 
        color gives the color pf the piece to play (1=white,-1=black)
        """

        (row,col) = move

        # Add the piece to the empty square.
        assert self[row][col] == 0
        self[row][col] = color

