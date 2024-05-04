from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
from .TicTacToeTWGLogic import Board
import numpy as np

"""
Game class implementation for the game of TicTacToe on torus with gravity.
Based on the TicTacToeGame and was adapted to new rules.

Author: login, github
Date: Jan 5, 2018.

Based on the OthelloGame by Surag Nair.
"""
class TicTacToeTWGGame(Game):
    def __init__(self, rows=6, cols=7, win=4):
        self.rows = rows
        self.cols = cols
        if cols < rows:
            raise Exception('Invalid board configuration')

    def getInitBoard(self):
        # return initial board (numpy board)
        b = Board(self.rows, self.cols)
        return b.pieces

    def getBoardSize(self):
        # (a,b) tuple
        return (self.rows, self.cols)

    def getActionSize(self):
        # return number of actions
        return (self.cols * self.rows) + 1

    def getNextState(self, board, player, action):
        # if player takes action on board, return next (board,player)
        # action must be a valid move
        if action == self.rows*self.cols:
            return (board, -player)
        b = Board(self.rows, self.cols)
        b.pieces = np.copy(board)
        move = (action%self.rows, int(action/self.rows))
        b.execute_move(move, player)
        return (b.pieces, -player)

    def getValidMoves(self, board, player):
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()
        b = Board(self.rows, self.cols)
        b.pieces = np.copy(board)
        legalMoves =  b.get_legal_moves(player)
        if len(legalMoves)==0:
            valids[-1]=1
            return np.array(valids)
        for row, col in legalMoves:
            valids[row + self.rows * col]=1
        return np.array(valids)

    def getGameEnded(self, board, player):
        # return 0 if not ended, 1 if player 1 won, -1 if player 1 lost
        # player = 1
        b = Board(self.rows, self.cols)
        b.pieces = np.copy(board)

        if b.is_win(player):
            return 1
        if b.is_win(-player):
            return -1
        if b.has_legal_moves():
            return 0
        # draw has a very little value 
        return 1e-4

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        return player*board

    def getSymmetries(self, board, pi):
        # mirror, rotational
        assert(len(pi) == self.getActionSize())  # 1 for pass
        pi_board = np.reshape(pi[:-1], (self.rows, self.cols))
        l = []

        for j in [True, False]:
            if j:
                newB = np.fliplr(board)
                newPi = np.fliplr(pi_board)
            else:
                newB = board.copy()
                newPi = pi_board.copy()
            l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l

    def stringRepresentation(self, board):
        # 8x8 numpy array (canonical board)
        return board.tostring()

    @staticmethod
    def display(board):
        display_pieces = board.astype(str)
        display_pieces[board == 1] = 'X'
        display_pieces[board == -1] = 'O'
        display_pieces[board == 0] = ' '
        print(display_pieces)
        # return display_pieces

    @staticmethod
    def display_tg(board):
        display_pieces = board.astype(str)
        display_pieces[board == 1] = 'x'
        display_pieces[board == -1] = 'o'
        display_pieces[board == 0] = '  '
        return display_pieces