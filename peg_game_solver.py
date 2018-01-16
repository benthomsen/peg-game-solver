from __future__ import division
import numpy as np
from math import floor, ceil
from matplotlib import pyplot as plt

class Node(object):
    def __init__(self, state, parent=None, stateStr=None):
        self.parent = parent
        self.state = state
        self.stateStr = self.encodeState(state)

    def encodeState(self, state):
        # store state as a string for comparison
        stateStr = ''
        for row in range(5):
            for col in range(row + 1):
                stateStr += str(state[row, col])
        return stateStr

    def decodeState(self, stateStr):
        # restore numpy array from string
        state = 9 * np.ones((5, 5), dtype=int)
        pos = 0
        for row in range(5):
            for col in range(row + 1):
                state[row, col] = int(stateStr[pos])
                pos += 1
        return state

    def __str__(self):
        return self.genPrint(self.state)

    def genPrint(self, state):
        # print the node's state
        ret = ''
        for row in range(5):
            ret += '- ' * (5 - row)
            for col in range(row + 1):
                ret += str(state[row, col]) + ' - '
            ret += '- ' * (5 - row - 1) + '\n'
        ret += '\n'
        return ret

    def numPegs(self):
        # count the pegs in the current state
        count = 0
        for row in range(5):
            for col in range(row + 1):
                if (self.state[row, col] == 1):
                    count += 1
        return count

    def prettyPrint(self, ax, step):
        holes_x = np.zeros(15)
        holes_y = np.zeros(15)
        pegs_x = np.zeros(self.numPegs())
        pegs_y = np.zeros(self.numPegs())

        if self.parent is not None:
            change_x = []
            change_y = []

        ctr_p = 0
        ctr_h = 0
        for row in range(5):
            for col in range(row + 1):
                holes_x[ctr_h] = (5 - row) + 2 * col
                holes_y[ctr_h] = 5 - row
                if (self.state[row, col] == 1):
                    pegs_x[ctr_p] = (5 - row) + 2 * col
                    pegs_y[ctr_p] = 5 - row
                    ctr_p += 1
                if self.parent is not None:
                    if (self.state[row, col] != self.parent.state[row, col]):
                        change_x.append((5 - row) + 2 * col)
                        change_y.append(5 - row)
                ctr_h += 1

        #         plt.figure(figsize=(2,2))
        ax.scatter(holes_x, holes_y, s=45, c='grey')
        ax.scatter(pegs_x, pegs_y, s=30, c='r')
        if self.parent is not None:
            ax.plot(change_x, change_y, linestyle='dashed', c='r')
        ax.axis('off')
        ax.set_adjustable('box')
        ax.text(0, 4, 'Step: %d' % step)


#         plt.show()

class Game(object):

    def __init__(self, emptyloc):
        # create the first board state by placing the empty hole at desired location
        state = 9 * np.ones((5, 5), dtype=int)
        for row in range(5):
            for col in range(row + 1):
                state[row, col] = 1

        if emptyloc[1] > emptyloc[0]:
            raise IndexError("Invalid Empty Position")
        state[emptyloc[0], emptyloc[1]] = 0

        self.root = Node(state)
        self.start = emptyloc

    def __str__(self):
        return str(self.root)

    def validMoves(self, node):
        # take the current board state and find possible next steps
        children = []

        state = node.state

        for row in range(5):
            for col in range(1, row):
                # jump over from right to left
                if (state[row, col - 1] == 0) & (state[row, col] == 1) & (state[row, col + 1] == 1):
                    tmp = state.copy()
                    tmp[row, col - 1] = 1
                    tmp[row, col] = 0
                    tmp[row, col + 1] = 0
                    children.append(Node(tmp, parent=node))

                # jump over from left to right
                if (state[row, col - 1] == 1) & (state[row, col] == 1) & (state[row, col + 1] == 0):
                    tmp = state.copy()
                    tmp[row, col - 1] = 0
                    tmp[row, col] = 0
                    tmp[row, col + 1] = 1
                    children.append(Node(tmp, parent=node))

        for row in range(1, 4):
            for col in range(row):
                # jump over from top right to below left
                if (state[row - 1, col] == 1) & (state[row, col] == 1) & (state[row + 1, col] == 0):
                    tmp = state.copy()
                    tmp[row - 1, col] = 0
                    tmp[row, col] = 0
                    tmp[row + 1, col] = 1
                    children.append(Node(tmp, parent=node))

                # jump over from below left to above right
                if (state[row - 1, col] == 0) & (state[row, col] == 1) & (state[row + 1, col] == 1):
                    tmp = state.copy()
                    tmp[row - 1, col] = 1
                    tmp[row, col] = 0
                    tmp[row + 1, col] = 0
                    children.append(Node(tmp, parent=node))

            for col in range(1, row + 1):
                # jump over from top left to below right
                if (state[row - 1, col - 1] == 1) & (state[row, col] == 1) & (state[row + 1, col + 1] == 0):
                    tmp = state.copy()
                    tmp[row - 1, col - 1] = 0
                    tmp[row, col] = 0
                    tmp[row + 1, col + 1] = 1
                    children.append(Node(tmp, parent=node))

                # jump over from below right to top left
                if (state[row - 1, col - 1] == 0) & (state[row, col] == 1) & (state[row + 1, col + 1] == 1):
                    tmp = state.copy()
                    tmp[row - 1, col - 1] = 1
                    tmp[row, col] = 0
                    tmp[row + 1, col + 1] = 0
                    children.append(Node(tmp, parent=node))

        return children

    def DFS(self, root):
        # carry out depth first search:
        # expand valid moves from init
        # continue expanding until no valid moves from state
        # if number of pegs left is 1, then return path
        # otherwise backtrack

        curr = root
        Q = [curr]
        while len(Q) > 0:
            curr = Q.pop()
            if curr.numPegs() == 1:
                return curr
            else:
                N = self.validMoves(curr)
                for n in N:
                    new = True
                    for q in Q:
                        if n.stateStr == q.stateStr:
                            new = False
                            break
                    if new:
                        Q.append(n)
        return curr

    def DFSHard(self, root):
        # version where peg must be in spot which was empty to start

        curr = root
        Q = [curr]
        while len(Q) > 0:
            curr = Q.pop()
            if (curr.numPegs() == 1) & (curr.state[self.start[0], self.start[1]] == 1):
                return curr
            else:
                N = self.validMoves(curr)
                for n in N:
                    new = True
                    for q in Q:
                        if n.stateStr == q.stateStr:
                            new = False
                            break
                    if new:
                        Q.append(n)
        return curr

    def prettyPrintPath(self, slist):
        l = len(slist)
        f, axarr = plt.subplots(int(ceil(l / 4)), 4, figsize=(12, 9))
        for ind, s in enumerate(slist):
            x = int(floor(ind / 4))
            y = int(ind % 4)
            s.prettyPrint(axarr[x][y], ind)
        for extra in range(l, int(ceil(l / 4) * 4)):
            x = int(floor(extra / 4))
            y = int(extra % 4)
            axarr[x][y].axis('off')

        plt.show()

    def solveBoard(self):
        print "Starting"
        solved = self.DFS(self.root)
        if (solved.numPegs() == 1):
            print "Success! Found a solution."
        else:
            print "Failure! Didn't find a solution."
        solvedlist = []
        while solved.parent is not None:
            solvedlist.append(solved)
            solved = solved.parent
        solvedlist.append(self.root)

        #         for s in solvedlist[::-1]:
        #             print s
        self.prettyPrintPath(solvedlist[::-1])

    def solveBoardHard(self):
        print "Starting"
        solved = self.DFSHard(self.root)
        if (solved.numPegs() == 1):
            print "Success! Found a solution."
        else:
            print "Failure! Didn't find a solution."

        solvedlist = []
        while solved.parent is not None:
            solvedlist.append(solved)
            solved = solved.parent
        solvedlist.append(self.root)

        #         for s in solvedlist[::-1]:
        #             print s
        self.prettyPrintPath(solvedlist[::-1])


if __name__ == '__main__':
    row_raw = raw_input("Row of empty hole (1 to 5): ")
    try:
        row = int(row_raw)
    except ValueError:
        row = 1
    print row, '\n'

    col_raw = raw_input("Column of empty hole (1 to row): ")
    try:
        col = int(col_raw)
    except ValueError:
        col = 1
    print col, '\n'

    mode = raw_input("Want last peg in starting hole? [y/(n)]\n")
    print mode, '\n'
    game = Game((row-1, col-1))

    if mode in ("yes", "y", "Y", "Yes"):
        game.solveBoardHard()
    else:
        game.solveBoard()
