import random

from libs import *


class Board(object):
    def __init__(self, base_board):
        self.board = base_board.copy()
        self.generate_cells()
        self.stats = None
    def get_start(self):
        return np.argwhere(self.board == 2)[0]

    def get_end(self):
        return np.argwhere(self.board == 3)[0]


    def list_one_sum(self, l):
        l = [x / sum(l) for x in l]
        return l
    def generate_cells(self):
        for y in range(self.board.shape[1]):
            for x in range(self.board.shape[0]):
                self.board[y][x] = random.choice([0,1])
        start = random.randint(0, self.board.shape[0]-1), random.randint(0, self.board.shape[1]-1)
        end = random.randint(0, self.board.shape[0]-1), random.randint(0, self.board.shape[1]-1)
        while end==start:
            end = random.randint(0, self.board.shape[0]-1), random.randint(0, self.board.shape[1]-1)

        self.board[start[1]][start[0]] = 2
        self.board[end[1]][end[0]] = 3

    def render(self, width, height):
        surf = pygame.Surface((width, height))
        for y in range(self.board.shape[1]):
            for x in range(self.board.shape[0]):
                rect = (width / self.board.shape[0], height / self.board.shape[1])
                pygame.draw.rect(surf, (100, 100, 100), (rect[0] * x, rect[1] * y, rect[0], rect[1]), 1)
                cell = self.board[x][y]
                if cell == 1: # wall
                    pygame.draw.rect(surf, (255, 0, 0), (rect[0] * x, rect[1] * y, rect[0], rect[1]))
                if cell == 2: # wall
                    pygame.draw.rect(surf, (0, 255, 0), (rect[0] * x, rect[1] * y, rect[0], rect[1]))
                if cell == 3: # wall
                    pygame.draw.rect(surf, (0, 0, 255), (rect[0] * x, rect[1] * y, rect[0], rect[1]))
        return surf