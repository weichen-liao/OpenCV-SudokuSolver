# -*- coding: utf-8 -*-
# Author: Weichen Liao

import numpy as np
from google.cloud import vision
import io
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from copy import deepcopy
import glob
import random
from SudokuSolver import SudokuPipeline
import signal

SCREENSHOT_PATH = 'sudoku_imgs/screenshot_temp.png'
FONT = './font/arial.ttf'
COLOR_GREEN = (67, 212, 51)
COLOR_BLUE = (3, 127, 252)
COLOR_RED = (255, 0, 0)


class TimeoutException(Exception):   # Custom exception class
    pass

def timeout_handler(signum, frame):   # Custom signal handler
    raise TimeoutException

# predict a image from local system using google vision api
def detect_text(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    print(type(image))

    response = client.text_detection(image=image)
    texts = response.text_annotations
    if len(texts) == 0 or len(texts) == 1:
        return []

    res = []
    grid = texts[0]
    coor_lefttop = (grid.bounding_poly.vertices[0].x, grid.bounding_poly.vertices[0].y)
    grid_len = grid.bounding_poly.vertices[1].x - grid.bounding_poly.vertices[0].x
    grid_hgt = grid.bounding_poly.vertices[2].y - grid.bounding_poly.vertices[1].y
    grid_info = [coor_lefttop, grid_len, grid_hgt]
    res.append(grid_info)

    for text in texts[1:]:
        content = text.description
        coor_lefttop = (text.bounding_poly.vertices[0].x, text.bounding_poly.vertices[0].y)
        box_len = text.bounding_poly.vertices[1].x - text.bounding_poly.vertices[0].x
        box_hgt = text.bounding_poly.vertices[2].y - text.bounding_poly.vertices[1].y
        # google vision api will identify closely attached strings as a whole, in this case, separate them apart.
        if len(content) > 1:
            gap_x = box_len / len(content)
            for i, c in enumerate(content):
                coor_new = (coor_lefttop[0] + gap_x * i, coor_lefttop[1])
                if c not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                    continue
                else:
                    box_info = [c, coor_new, gap_x, box_hgt]
                    res.append(box_info)
            pass
        else:
            if content not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                continue
            box_info = [content, coor_lefttop, box_len, box_hgt]
            res.append(box_info)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return res

# given predicted result and matplotlib ax, return modified ax, and the grid information
def add_rect_pil(input_info, image):
    if len(input_info) == 0:
        return image, None, None, None
    predicts = deepcopy(input_info)
    grid_info = predicts[0]
    grid_len = grid_info[1]
    grid_hgt = grid_info[2]
    gap_x = grid_len/9
    gap_y = grid_hgt/9
    # make slight extension of the grid
    extension_x = gap_x/3
    extension_y = gap_y/3
    grid_info[0] = (grid_info[0][0]-extension_x, grid_info[0][1]-extension_y)
    # adjust the length, height and gap
    grid_len += 2*extension_x
    grid_hgt += 2*extension_y
    gap_x = grid_len/9
    gap_y = grid_hgt/9

    draw = ImageDraw.Draw(image)
    fnt = ImageFont.truetype(FONT, size=50)

    # draw the grid
    for i in range(10):
        # draw the row lines
        draw.line((grid_info[0][0], grid_info[0][1] + i*gap_y, grid_info[0][0]+grid_len, grid_info[0][1]+i*gap_y), fill=COLOR_RED, width=2)
        # draw the col lines:
        draw.line((grid_info[0][0] + i * gap_x, grid_info[0][1], grid_info[0][0] + i * gap_x, grid_info[0][1] + grid_hgt),fill=COLOR_RED, width=2)

    # draw the digit detected
    # for item in predicts[1:]:
    #     draw.text((item[1][0], item[1][1]), item[0], fill=(3, 127, 252), font=fnt)
        # draw.line((item[1][0], item[1][1], item[1][0], item[1][1] + item[2]),fill=(3, 127, 252), width=2)
        # draw.line((item[1][0], item[1][1], item[1][0] + item[3], item[1][1]), fill=(3, 127, 252), width=2)
        # draw.line((item[1][0], item[1][1] + item[2], item[1][0] + item[3], item[1][1] + item[2]), fill=(3, 127, 252), width=2)
        # draw.line((item[1][0] + item[3], item[1][1], item[1][0] + item[3], item[1][1] + item[2]), fill=(3, 127, 252), width=2)

    grid_lefttop = (grid_info[0][0], grid_info[0][1])
    return image, grid_lefttop, grid_len, grid_hgt


def get_cell_centers(grid_lefttop, grid_len, grid_hgt):
    centers = []
    gap_x = grid_len / 9
    gap_y = grid_hgt / 9
    for i in range(9):
        for j in range(9):
            cell_center = [grid_lefttop[0] + gap_x/2 + i*gap_x, grid_lefttop[1] + gap_y/2 + j*gap_y]
            centers.append(cell_center)
    return centers

# load saved screenshot from local system, modify it, and save it again
def modify_screenshot_new(predicts, path=SCREENSHOT_PATH):
    image = Image.open(path)
    # display the detected digits in the grid
    image, grid_lefttop, grid_len, grid_hgt = add_rect_pil(predicts, image)

    # is any digits detected
    if grid_lefttop:
        # generate the matrix for sudoku solving
        mat = generate_matrix(predicts, grid_lefttop, grid_len, grid_hgt)
        mat_ori = deepcopy(mat)
        print('Scanned mat:')
        print(np.array(mat).T)
        if isinstance(mat, str):
            return image
        # display the scanned digits
        digits_to_show_scanned = []
        for i in range(9):
            for j in range(9):
                if mat_ori[i][j] != 0:
                    digits_to_show_scanned.append([i, j, mat_ori[i][j]])
        image = show_digit(image=image, digits_to_show=digits_to_show_scanned, grid_lefttop=grid_lefttop, gap_x=grid_len / 9, gap_y=grid_hgt / 9, color=COLOR_BLUE)

        signal.signal(signal.SIGALRM, timeout_handler)
        # Start the timer. Once 1 seconds are over, a SIGALRM signal is sent.
        signal.alarm(1)
        try:
            mat_solved = SudokuPipeline(mat)
        except TimeoutException:
            mat_solved = 'Time out'
            print(mat_solved)
            return image
        else:
            # Reset the alarm
            signal.alarm(0)
        # display the solved matrix on image
        if isinstance(mat_solved, str) == False:
            print('Solved mat')
            print(np.array(mat_solved).T)
            # first, conclude which digits to display
            digits_to_show_detected = []
            for i in range(9):
                for j in range(9):
                    if mat_ori[i][j] == 0:
                        digits_to_show_detected.append([i,j,mat_solved[i][j]])
            image = show_digit(image=image, digits_to_show=digits_to_show_detected, grid_lefttop=grid_lefttop, gap_x=grid_len/9, gap_y=grid_hgt/9)

            # save screenshots if you want
            image.save('sudoku_imgs/final_picture'+str(random.randint(1, 1000))+'.png')

    return image

def show_digit(image, digits_to_show, grid_lefttop, gap_x, gap_y, color=COLOR_GREEN):
    draw = ImageDraw.Draw(image)
    fnt = ImageFont.truetype(FONT, size=int(gap_x*0.6))
    for item in digits_to_show:
        i, j, digit = item[0], item[1], item[2]
        draw.text((grid_lefttop[0] + i*gap_x + gap_x/3, grid_lefttop[1]+ j*gap_y + gap_y/3), str(digit), fill=color, font=fnt)
    return image

def generate_matrix(predicts, grid_lefttop, grid_len, grid_hgt):
    # initialize the matrix
    mat = [[0 for i in range(9)] for j in range(9)]

    gap_x = grid_len / 9
    gap_y = grid_hgt / 9
    print('gap_x:', gap_x, 'gap_y:', gap_y)
    for item in predicts[1:]:
        coor = item[1]
        index_x = int((coor[0] + gap_x / 3 - grid_lefttop[0]) / gap_x)
        index_y = int((coor[1] + gap_y / 3 - grid_lefttop[1]) / gap_y)
        index_x = max(0, index_x)
        index_x = min(8, index_x)
        index_y = max(0, index_y)
        index_y = min(8, index_y)
        # the index may exceed the limit because of recognition inaccuary
        try:
            mat[index_x][index_y] = int(item[0])
        except:
            return 'error: fail to initialize the matrix'
    return mat