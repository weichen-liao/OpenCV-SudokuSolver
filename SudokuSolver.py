# -*- coding: utf-8 -*-
# Author: Weichen Liao
import numpy as np
import signal

class TimeoutException(Exception):   # Custom exception class
    pass

def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException

def findNextCellToFill(grid, i, j):
    for x in range(i, 9):
        for y in range(j, 9):
            if grid[x][y] == 0:
                return x, y
    for x in range(0, 9):
        for y in range(0, 9):
            if grid[x][y] == 0:
                return x, y
    return -1, -1


def isValid(grid, i, j, e):
    rowOk = all([e != grid[i][x] for x in range(9)])
    if rowOk:
        columnOk = all([e != grid[x][j] for x in range(9)])
        if columnOk:
            # finding the top left x,y co-ordinates of the section containing the i,j cell
            secTopX, secTopY = 3 * (i // 3), 3 * (j // 3)  # floored quotient should be used here.
            for x in range(secTopX, secTopX + 3):
                for y in range(secTopY, secTopY + 3):
                    if grid[x][y] == e:
                        return False
            return True
    return False


def solveSudoku(grid, i=0, j=0):
    i, j = findNextCellToFill(grid, i, j)
    if i == -1:
        return True
    for e in range(1, 10):
        if isValid(grid, i, j, e):
            grid[i][j] = e
            if solveSudoku(grid, i, j):
                return True
            # Undo the current cell for backtracking
            grid[i][j] = 0
    return False

def SudokuPipeline(matrix: list):
    try:
        solve = solveSudoku(matrix)
    except:
        return 'Failure'
    if solve == True:
        return np.array(matrix)
    else:
        return 'Failure'


if __name__ == '__main__':
    puzzle0 = [[5, 3, 0, 0, 7, 0, 0, 0, 0],
              [6, 0, 0, 1, 9, 5, 0, 0, 0],
              [0, 9, 8, 0, 0, 0, 0, 6, 0],
              [8, 0, 0, 0, 6, 0, 0, 0, 3],
              [4, 0, 0, 8, 0, 3, 0, 0, 1],
              [7, 0, 0, 0, 2, 0, 0, 0, 6],
              [0, 6, 0, 0, 0, 0, 2, 8, 0],
              [0, 0, 0, 4, 1, 9, 0, 0, 5],
              [0, 0, 0, 0, 8, 0, 0, 7, 9]]

    puzzle1 = [[0, 0, 7, 0, 0, 0, 0, 0, 0],
              [1, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 0, 4, 3, 0, 2, 0, 0],
              [0, 0, 0, 0, 0, 0, 0, 0, 6],
              [0, 0, 0, 5, 0, 9, 0, 0, 0],
              [0, 0, 0, 0, 0, 0, 4, 1, 8],
              [0, 0, 0, 0, 8, 1, 0, 0, 0],
              [0, 0, 2, 0, 0, 0, 0, 5, 0],
              [0, 4, 0, 0, 0, 0, 3, 0, 0]]

    puzzle2 = [[4, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 2, 0], [3, 0, 0, 0, 0, 8, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0], [2, 0, 0, 0, 4, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0, 0, 3], [0, 0, 0, 0, 1, 0, 0, 1, 0], [0, 6, 0, 0, 8, 0, 0, 0, 0]]

    signal.signal(signal.SIGALRM, timeout_handler)
    # Start the timer. Once 5 seconds are over, a SIGALRM signal is sent.
    signal.alarm(1)
    try:
        res = SudokuPipeline(puzzle1)
        print(res)
    except TimeoutException:
        print('time out')
        pass  # continue the for loop if function A takes more than 5 second
    else:
        # Reset the alarm
        signal.alarm(0)

