# A live camera Sudoku solver

This project tries to solve the Sudoku game by capturing images from camera.
the solved results will be directly displayed on the screen.

it looks like this:
![result2](https://github.com/weichen-liao/OpenCV-SudokuSolver/blob/main/result2.png)

or it can process the image from local file, and the result will be more accurate:
![result1](https://github.com/weichen-liao/OpenCV-SudokuSolver/blob/main/result1.png)


the digit detection is based on Google Vision API, you need to gain access to this API first. For the detail, check:  
https://cloud.google.com/vision/docs/ocr

methology:
the camera keeps capturing the screen, for each screen, try to detect digits using google API, if any digits found, draw a 9x9 grid according to the position of digits detected. Then try to solve the Sudoku game. It may fail to deliver the correct solution due to the inaccuracy of OCR, which may take a long time to solve the puzzle. So the strategy is to try maximum 1 second for each puzzle, if it exceed 1 second, then pass to the next frame.

requirement:
Python 3.8
OpenCV 4.5.1.48

run:
python3 main.py
