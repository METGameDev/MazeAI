import numpy as np

from libs import *

class AStar(object):
    def __init__(self, board):
        self.board = board
        self.start = [np.where(board == 2)[0][0], np.where(board == 2)[1][0]]
        self.end = [np.where(board == 3)[0][0], np.where(board == 3)[1][0]]
        self.cur = self.start.copy()
        #self.open = np.zeros((board.shape[0], board.shape[1], 3))
        self.openG = np.zeros((board.shape[0], board.shape[1]))
        self.openH = np.zeros((board.shape[0], board.shape[1]))
        self.openF = np.zeros((board.shape[0], board.shape[1]))

        #self.closed = np.zeros((board.shape[0], board.shape[1], 3))
        self.closedG = np.zeros((board.shape[0], board.shape[1]))
        self.closedH = np.zeros((board.shape[0], board.shape[1]))
        self.closedF = np.zeros((board.shape[0], board.shape[1]))

        self.found_end = False

        self.path = np.zeros((self.board.shape[0], self.board.shape[1]))

        self.impossible = False
        self.deadends = []
    def calc_G(self,pos):
        return math.hypot(self.start[0] - pos[0], self.start[1] - pos[1])
    def calc_H(self,pos):
        return math.hypot(self.end[0] - pos[0], self.end[1] - pos[1])
    def calc_F(self, pos):
        return self.calc_H(pos)+ self.calc_G(pos)

    def search_for_low(self, list, list2):

        lowest = float('inf')
        jk = np.argwhere(list != list2)
        for pos in jk:
            item = list[pos[0]][pos[1]]
            if item != 0 and item < lowest:
                lowest = item
        vals = np.argwhere(list == lowest)


        return vals




    def get_neighbors(self):
        neighbors = []
        for pos in [[1, 0], [-1, 0], [0, -1], [0, 1]]:
            nX = self.cur[0] + pos[0]
            nY = self.cur[1] + pos[1]
            if nX >= 0 and nY >= 0 and nX < self.board.shape[0] and nY < self.board.shape[1]:
                neighbors.append([nX, nY])
        return neighbors

    def set_costs(self, x, y):
        self.openG[x][y] = self.calc_G([x, y])
        self.openH[x][y] = self.calc_H([x, y])
        self.openF[x][y] = self.calc_F([x, y])

    def get_new_cur(self):
        # get lists of the costs
        #G_costs, H_costs, F_costs = self.costs_isolate(self.open)

        # get list of the lowest costs in each cost list
        # F takes priority over H, H over G, and G is final if the other two cant be decided
        try:
            f = self.search_for_low(self.openF, self.closedF)
            if len(f) == 1:
                c = f[0]
            else:
                h = self.search_for_low(self.openH, self.closedH)
                if len(h) == 1:
                    c = h[0]
                else:
                    c = self.search_for_low(self.openG, self.closedG)[0]
        except IndexError:
            self.impossible = True
            c = None
        return c

    def path_find(self):
        while True:

            # add to the open list based of the curNode
            neighbors = self.get_neighbors()
            for n in neighbors:
                # put costs into the open list if theres no wall
                if self.board[n[0]][n[1]] == 0:
                    self.set_costs(n[0], n[1])
                #check if the end is nearby
                if self.board[n[0]][n[1]] == 3:
                    #print("End Found!")
                    self.found_end = True


            #checking if the end has been found
            if self.found_end:
                self.cur = self.end.copy()
                self.path[self.cur[0]][self.cur[1]] = 1

                travelledSpots = []
                self.deadends = []

                while True:
                    neighbors = self.get_neighbors()
                    c = None
                    for x,y in neighbors:
                        if self.closedG[x][y] != 0:
                            if c == None or self.closedG[c[0]][c[1]] > self.closedG[x][y]:
                                if [x,y] not in travelledSpots and [x,y] not in self.deadends:
                                    c = [x,y]
                                    travelledSpots.append(c)
                        if self.board[x][y]==2:
                            self.path[x][y]=1
                            #print("Path Complete!")
                            return self.path
                    if c==None:
                        travelledSpots = []
                        self.deadends.append(self.cur)
                        self.cur = self.end.copy()
                        self.path = np.zeros((self.board.shape[0], self.board.shape[1]))
                    else:
                        self.cur = c
                    self.path[self.cur[0]][self.cur[1]] = 1


            old_cur = self.cur.copy()

            self.cur = self.get_new_cur()


            #check for impossibility
            if type(self.cur) == type(None) or (self.cur[0]==old_cur[0] and self.cur[1]==old_cur[1]):
                self.impossible = True
            if len(np.unique(self.closedF)) == len(np.unique(self.openF)): self.impossible = True
            if self.impossible:
                #print("Impossible Path!")
                return None

            # mark the current node as closed
            self.closedG[self.cur[0]][self.cur[1]] = self.openG[self.cur[0]][self.cur[1]]
            self.closedH[self.cur[0]][self.cur[1]] = self.openH[self.cur[0]][self.cur[1]]
            self.closedF[self.cur[0]][self.cur[1]] = self.openF[self.cur[0]][self.cur[1]]


    def stats(self):
        #only call once the pathfinding is done
        stats = {"steps": np.sum(self.path),
                 "walls": np.sum(self.board == 1),
                 "air": np.sum(self.board == 0),
                 "deadends":len(self.deadends),
                 "path":self.path}
        return stats





