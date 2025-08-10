import numpy as np
import copy

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
    parts = fen.split()
    board_part = parts[0]
    ToMove =  parts[1]  # 'w' or 'b'

    pieces = np.zeros((8, 8), dtype=np.int16)

    rows = board_part.split('/')
    for row_idx, row in enumerate(rows):
        col_idx = 0
        for char in row:
            if char.isdigit():
                col_idx += int(char)
            else:
                pieces[col_idx][row_idx] = pieceChr.index(char) + 1
                col_idx += 1

    return pieces, ToMove

def MoveGenRook(BoardState, StartSquare, pieceColor, piece_type):
    RookMoves = []
    x, y = StartSquare
    directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
    for dx, dy in directions:
        step = 1
        while True:
            nx, ny = x + dx * step, y + dy * step
            if not (0 <= nx < 8 and 0 <= ny < 8):
                break
            target_piece = BoardState[nx][ny]
            if target_piece == 0:
                RookMoves.append((nx, ny))
            elif pieceColor == 0 and target_piece >= 7:
                RookMoves.append((nx, ny))
                break
            elif pieceColor == 1 and 1 <= target_piece <= 6:
                RookMoves.append((nx, ny))
                break
            else:
                break
            step += 1
    return RookMoves


def MoveGenBishop(BoardState, StartSquare, pieceColor, piece_type):
    BishopMoves = []
    x, y = StartSquare
    directions = [(1, -1), (-1, -1), (1, 1), (-1, 1)]  # diag with up = -y
    for dx, dy in directions:
        step = 1
        while True:
            nx, ny = x + dx * step, y + dy * step
            if not (0 <= nx < 8 and 0 <= ny < 8):
                break
            target_piece = BoardState[nx][ny]
            if target_piece == 0:
                BishopMoves.append((nx, ny))
            elif pieceColor == 0 and target_piece >= 7:
                BishopMoves.append((nx, ny))
                break
            elif pieceColor == 1 and 1 <= target_piece <= 6:
                BishopMoves.append((nx, ny))
                break
            else:
                break
            step += 1
    return BishopMoves


def MoveGenQueen(BoardState, StartSquare, pieceColor, piece_type):
    return MoveGenRook(BoardState, StartSquare, pieceColor, piece_type) + \
           MoveGenBishop(BoardState, StartSquare, pieceColor, piece_type)


def MoveGenKnight(BoardState, StartSquare, pieceColor, piece_type):
    KnightMoves = []
    x, y = StartSquare
    jumps = [(2, 1), (1, 2), (-1, 2), (-2, 1),
             (-2, -1), (-1, -2), (1, -2), (2, -1)]
    for dx, dy in jumps:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 8 and 0 <= ny < 8:
            target_piece = BoardState[nx][ny]
            if target_piece == 0:
                KnightMoves.append((nx, ny))
            elif pieceColor == 0 and target_piece >= 7:
                KnightMoves.append((nx, ny))
            elif pieceColor == 1 and 1 <= target_piece <= 6:
                KnightMoves.append((nx, ny))
    return KnightMoves


def MoveGenKing(BoardState, StartSquare, pieceColor, piece_type):
    KingMoves = []
    x, y = StartSquare
    steps = [(1, 0), (-1, 0), (0, -1), (0, 1),
             (1, -1), (-1, -1), (1, 1), (-1, 1)]
    for dx, dy in steps:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 8 and 0 <= ny < 8:
            target_piece = BoardState[nx][ny]
            if target_piece == 0:
                KingMoves.append((nx, ny))
            elif pieceColor == 0 and target_piece >= 7:
                KingMoves.append((nx, ny))
            elif pieceColor == 1 and 1 <= target_piece <= 6:
                KingMoves.append((nx, ny))
    return KingMoves


def MoveGenPawn(BoardState, StartSquare, pieceColor, piece_type):
    PawnMoves = []
    x, y = StartSquare

    if pieceColor == 0:  # white moves UP (-y)
        if y - 1 >= 0 and BoardState[x][y - 1] == 0:
            PawnMoves.append((x, y - 1))
            if y == 6 and BoardState[x][y - 2] == 0:
                PawnMoves.append((x, y - 2))
        for dx in (-1, 1):
            nx, ny = x + dx, y - 1
            if 0 <= nx < 8 and 0 <= ny < 8:
                target_piece = BoardState[nx][ny]
                if target_piece >= 7:
                    PawnMoves.append((nx, ny))

    else:  # black moves DOWN (+y)
        if y + 1 < 8 and BoardState[x][y + 1] == 0:
            PawnMoves.append((x, y + 1))
            if y == 1 and BoardState[x][y + 2] == 0:
                PawnMoves.append((x, y + 2))
        for dx in (-1, 1):
            nx, ny = x + dx, y + 1
            if 0 <= nx < 8 and 0 <= ny < 8:
                target_piece = BoardState[nx][ny]
                if 1 <= target_piece <= 6:
                    PawnMoves.append((nx, ny))

    return PawnMoves

def GetPieceColor(piece):
    return "w" if piece < 7 else "b"

def GetPieceType(piece):
    if piece == 0:
        return None  # empty square

    # Piece types in order: King, Queen, Bishop, Knight, Rook, Pawn
    types = ["K", "Q", "B", "N", "R", "P"]

    return types[(piece - 1) % 6]


def ColorCHRtoNUM(COLORchr):
    return 0 if COLORchr == "w" else 1    

def ColorNUMtoCHR(COLORnum):
    return "w" if COLORnum == 0 else "b"  

def InCheck(BoardState, Color):
    # Color: 0=white, 1=black
    OpponentColor = 1 if Color == 0 else 0

    AttackedSquares = GetAttackedSquares(BoardState, OpponentColor)

    # Find king position of 'Color'
    for x in range(8):
        for y in range(8):
            piece = BoardState[x][y]
            if GetPieceType(piece) == "K" and GetPieceColor(piece) == ColorNUMtoCHR(Color):
                KingPos = (x, y)
                break

    # If king pos is in attacked squares -> check
    if KingPos in AttackedSquares:
        return True
    return False

def IsMate(BoardState):
    #returns a color if it is mate or "" if not

    for color in ["w","b"]:
        TotalValidMoves = 0
        for x,row in enumerate(BoardState):
            for y,piece in enumerate(row):
                if GetPieceColor(piece) == color and piece > 0:
                    TotalValidMoves += len(ValidMoves(BoardState,(x,y),piece,color))
        if TotalValidMoves == 0 and InCheck(BoardState,ColorCHRtoNUM(color)):
            return color
    return ""

def IsStaleMate(BoardState):
    #returns a color if it is stalemate or "" if not

    for color in ["w","b"]:
        TotalValidMoves = 0
        for x,row in enumerate(BoardState):
            for y,piece in enumerate(row):
                if GetPieceColor(piece) == color and piece > 0:
                    TotalValidMoves += len(ValidMoves(BoardState,(x,y),piece,color))
        if TotalValidMoves == 0 and not InCheck(BoardState,ColorCHRtoNUM(color)):
            return color
    return ""

def GetAttackedSquares(BoardState, Color):
    move_generators = {
        1: MoveGenKing,   7: MoveGenKing,
        2: MoveGenQueen,  8: MoveGenQueen,
        3: MoveGenBishop, 9: MoveGenBishop,
        4: MoveGenKnight, 10: MoveGenKnight,
        5: MoveGenRook,   11: MoveGenRook,
        6: MoveGenPawn,   12: MoveGenPawn
    }

    AttackedSquares = []

    for x, row in enumerate(BoardState):
        for y, piece in enumerate(row):
            if piece != 0 and ColorCHRtoNUM(GetPieceColor(piece)) == Color:
                # Get pseudo-legal moves without checking for king safety
                AttackedSquares.extend(
                    move_generators[piece](BoardState, (x,y), Color, piece)
                )

    return AttackedSquares

def ValidMoves(BoardState, StartSquare, piece_type, ToMove):
    pieceColor = ColorCHRtoNUM(GetPieceColor(piece_type)) # 0 or 1

    move_generators = {
        1: MoveGenKing,   7: MoveGenKing,
        2: MoveGenQueen,  8: MoveGenQueen,
        3: MoveGenBishop, 9: MoveGenBishop,
        4: MoveGenKnight, 10: MoveGenKnight,
        5: MoveGenRook,   11: MoveGenRook,
        6: MoveGenPawn,   12: MoveGenPawn
    }


    ValidPieceMoves = []

    for move in move_generators[piece_type](BoardState, StartSquare, pieceColor, piece_type):
        DummyBoard = copy.deepcopy(BoardState)
        DummyBoard[StartSquare[0]][StartSquare[1]] = 0
        DummyBoard[move[0]][move[1]] = piece_type

        if not InCheck(DummyBoard, pieceColor):
            ValidPieceMoves.append(move)

    return ValidPieceMoves



if __name__ == '__main__':
    __init__()
    print(Readfen("rnbqkbnr/8/8/8/8/8/PPPPPPPP/RNBQKBNR"))