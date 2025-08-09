import numpy as np

def __init__():
    global pieceChr
    pieceChr = [
    "K",
    "Q",
    "B",
    "N",
    "R",
    "P",
    "k",
    "q",
    "b",
    "n",
    "r",
    "p"]


def Readfen(fen):
    pieces = np.zeros((8,8),dtype=np.int16)
    row_counter = 0
    col_counter = 0

    for chr in fen:
        if chr in pieceChr:
            pieces[col_counter][row_counter] = pieceChr.index(chr) + 1
            col_counter += 1
        elif chr == "/":
            col_counter = 0
            row_counter += 1
        else:
            col_counter += int(chr)

    return pieces


#movegen


if __name__ == '__main__':
    __init__()
    print(Readfen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"))