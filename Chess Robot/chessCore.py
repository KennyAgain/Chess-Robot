import numpy as np
import copy
import subprocess


def __init__():
    global pieceChr
    global MaterialValue
    global kingPos

    result = subprocess.run(
    ["dotnet", "run", "--project", "ChessCoreFast/ChessCoreFast.csproj", "-c", "Release"],
    capture_output=True, text=True
    )

    print(result.stdout)

    kingPos = {"w": (7, 4), "b": (0, 4)}

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

    MaterialValue = [
        0,  # 0 - empty
        100,  # 1 - White King
        9,  # 2 - White Queen
        3,  # 3 - White Bishop
        3,  # 4 - White Knight
        5,  # 5 - White Rook
        1,  # 6 - White Pawn
        100,  # 7 - Black King
        9,  # 8 - Black Queen
        3,  # 9 - Black Bishop
        3,  # 10 - Black Knight
        5,  # 11 - Black Rook
        1,  # 12 - Black Pawn
    ]

import time

class Timer:
    def __init__(self):
        self.lasttime = time.time()

    def time_since_last_call(self):
        now = time.time()
        elapsed = now - self.lasttime
        self.lasttime = now
        return elapsed



def Readfen(fen):
    global kingPos
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
                if char == "k": kingPos["b"] = (col_idx,row_idx)
                if char == "K": kingPos["w"] = (col_idx,row_idx)
                pieces[col_idx][row_idx] = pieceChr.index(char) + 1
                col_idx += 1

    return pieces, ToMove

def CreateFen(BoardState, ToMove, EnPassant="-", Halfmove="0", Fullmove="1"):
    """
    Creates a FEN string from a numeric board representation that is rotated 90°.
    """

    fen_rows = []
    # Loop from rank 8 to rank 1
    for rank in range(8):
        empty_count = 0
        fen_row = ""
        # Now rank index comes from *columns* in your board
        for file in range(8):
            # Transpose + flip vertical to get correct FEN orientation
            piece = BoardState[file][rank]
            if piece == 0:
                empty_count += 1
            else:
                if empty_count > 0:
                    fen_row += str(empty_count)
                    empty_count = 0
                piece_letter = GetPieceType(piece)
                if GetPieceColor(piece) == "b":
                    piece_letter = piece_letter.lower()
                fen_row += piece_letter
        if empty_count > 0:
            fen_row += str(empty_count)
        fen_rows.append(fen_row)

    fen_board = "/".join(fen_rows)

    # Detect castling rights from your rotated board
    castling = ""
    # White kingside
    if BoardState[7][4] == 1 and BoardState[7][7] == 5:
        castling += "K"
    # White queenside
    if BoardState[7][4] == 1 and BoardState[7][0] == 5:
        castling += "Q"
    # Black kingside
    if BoardState[0][4] == 7 and BoardState[0][7] == 11:
        castling += "k"
    # Black queenside
    if BoardState[0][4] == 7 and BoardState[0][0] == 11:
        castling += "q"

    if castling == "":
        castling = "-"

    return f"{fen_board} {ToMove} {castling} {EnPassant} {Halfmove} {Fullmove}"



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

def InCheck(Board,color):
    global kingPos
    kx,ky=kingPos[color]
    opp="b" if color=="w" else "w"
    return (kx,ky) in GetAttackedSquares(Board,opp)

def IsMate(BoardState):
    #returns a color if it is mate or "" if not

    for color in ["w","b"]:
        TotalValidMoves = ValidMoves(BoardState,color)
        if TotalValidMoves == 0 and InCheck(BoardState,color):
            return color
    return ""

def IsStaleMate(BoardState):
    #returns a color if it is stalemate or "" if not

    for color in ["w","b"]:
        TotalValidMoves = 0
        for x,row in enumerate(BoardState):
            for y,piece in enumerate(row):
                if GetPieceColor(piece) == color and piece > 0:
                    TotalValidMoves += len(ValidPieceMoves(BoardState,(x,y),piece,color))
        if TotalValidMoves == 0 and not InCheck(BoardState,color):
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
            if piece != 0 and GetPieceColor(piece) == Color:
                # Get pseudo-legal moves without checking for king safety
                AttackedSquares.extend(
                    move_generators[piece](BoardState, (x,y), ColorCHRtoNUM(Color), piece)
                )

    return AttackedSquares

def MakeMove(BoardState,StartSquare,EndSquare):
    global kingPos
    Capture = BoardState[EndSquare[0]][EndSquare[1]]

    # Handle pawn promotion
    piece = BoardState[StartSquare[0]][StartSquare[1]]
    if (EndSquare[1] == 0 or EndSquare[1] == 7) and GetPieceType(piece) == "P":
        if GetPieceColor(piece) == "w":
            BoardState[EndSquare[0]][EndSquare[1]] = 2  # promote to Queen
        else:
            BoardState[EndSquare[0]][EndSquare[1]] = 8  # promote to Queen
    else:
        BoardState[EndSquare[0]][EndSquare[1]] = piece

    BoardState[StartSquare[0]][StartSquare[1]] = 0

    # Update king position if moved
    moved_piece = BoardState[EndSquare[0]][EndSquare[1]]
    if GetPieceType(moved_piece) == "K":
        color = GetPieceColor(moved_piece)  # "w" or "b"
        kingPos[color] = EndSquare

    return BoardState, Capture

def ValidMoves(BoardState,ToMove):
    #returns a list of all valid moves for the given color. example : [((0,0),(1,1)),]
    ValidMoves = []
    for x,row in enumerate(BoardState):
        for y,piece in enumerate(row):
            if GetPieceColor(piece) == ToMove and piece > 0:
                PieceMoves = ValidPieceMoves(BoardState,(x,y),piece,ToMove)
                if len(PieceMoves) > 0:
                    for move in PieceMoves:
                        ValidMoves.append(((x,y),(move)))
    return ValidMoves


def ValidPieceMoves(BoardState, StartSquare, piece_type, ToMove):
    global kingPos
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
        tempKingPos = kingPos.copy()
    
        # if king moves, update king position
        if GetPieceType(piece_type) == "K":
            kingPos[ColorNUMtoCHR(pieceColor)] = move
    
        # save old pieces for undo
        captured_piece = BoardState[move[0]][move[1]]
        moving_piece = BoardState[StartSquare[0]][StartSquare[1]]
    
        # make move in-place
        BoardState[StartSquare[0]][StartSquare[1]] = 0
        BoardState[move[0]][move[1]] = moving_piece
    
        # check legality
        if not InCheck(BoardState, ColorNUMtoCHR(pieceColor)):
            ValidPieceMoves.append(move)
    
        # undo move
        BoardState[StartSquare[0]][StartSquare[1]] = moving_piece
        BoardState[move[0]][move[1]] = captured_piece
        kingPos = tempKingPos


    return ValidPieceMoves




if __name__ == '__main__':
    __init__()
    print(Readfen("rnbqkbnr/8/8/8/8/8/PPPPPPPP/RNBQKBNR"))