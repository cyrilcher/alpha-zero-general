import numpy as np

"""
Random and Human-ineracting players for the game of TicTacToe.

Author: Evgeny Tyurin, github.com/evg-tyurin
Date: Jan 5, 2018.

Based on the OthelloPlayers by Surag Nair.

"""
class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        a = np.random.randint(self.game.getActionSize())
        valids = self.game.getValidMoves(board, 1)
        while valids[a]!=1:
            a = np.random.randint(self.game.getActionSize())
        return a


class HumanTicTacToePlayer():
    def __init__(self, game):
        self.game = game

    def play(self, board):
        # display(board)
        valid = self.game.getValidMoves(board, 1)
        for i in range(len(valid)):
            if valid[i]:
                print(i%self.game.rows, int(i/self.game.rows))
        while True: 
            # Python 3.x
            a = input()
            # Python 2.x 
            # a = raw_input()
            if a == 'quit':
                raise Exception('Game quited')
            try:
                row, col = [int(x) for x in a.split(' ')] #x: row, y: col
                a = self.game.rows * col + row if row != -1 else self.game.rows * self.game.cols
                assert valid[a] == 1
                break
            except:
                print('Invalid')

        return a
