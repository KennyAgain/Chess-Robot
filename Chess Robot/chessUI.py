import pygame
import chessAI
import chessCore
import chessRobotCom
import copy
import time

import random

pygame.init()
chessCore.__init__()



#COLORS
LightSquares = (220, 200, 160)  # default lichess light square
DarkSquares = (160, 120, 80)  # default lichess dark square

W,H = 1000,800
screen = pygame.display.set_mode((W,H))
pygame.display.set_caption("Chess Board")

clock = pygame.time.Clock()


piece_Image = pygame.image.load("Chess Robot\pieces.png").convert_alpha()
piece_Image = pygame.transform.scale(piece_Image,(H/8*6,H/8*2))

p_w, p_h = piece_Image.get_size()

def CreatePieceMasks():
    PieceWidth = p_w / 6
    PieceHeight = p_h / 2

    PieceMasks= []

    for Color in range(2):
        for Type in range(6):
            PieceMask = pygame.Rect(Type*PieceWidth,Color*PieceHeight,PieceWidth,PieceHeight)

            PieceMasks.append(PieceMask)
    return PieceMasks

def DrawBoard(screen):
    stepPerField = H / 8
    for row in range(8):
        for column in range(8):
            if (row + column) % 2 == 0: FieldColor = LightSquares 
            else: FieldColor = DarkSquares

            pygame.draw.rect(screen,FieldColor,(row*stepPerField,column*stepPerField,stepPerField,stepPerField))


def DrawPieces(screen,pieces,mouse_pos):
    stepPerField = H / 8
    for row in range(8):
        for column in range(8):
            
            if pieces[row][column] > 0:
                screen.blit(piece_Image,(row*stepPerField,column*stepPerField),PieceMasks[pieces[row][column]-1])
    
    if piecepickedup > -1: #draw picked up piece
        screen.blit(piece_Image,(mouse_pos[0] - stepPerField/2,mouse_pos[1] - stepPerField/2),PieceMasks[piecepickedup - 1])
    
def DrawValidMoves(screen,valid_moves):
    stepPerField = H / 8
    for move in valid_moves:
        pygame.draw.circle(screen,(64, 166, 226),(move[0] * stepPerField + stepPerField/2, move[1] * stepPerField + stepPerField / 2),stepPerField / 4)


def CheckFieldClicked(mouse_pos):
    stepPerField = H / 8
    for row in range(8):
        for column in range(8):
            if pygame.Rect(row*stepPerField,column*stepPerField,stepPerField,stepPerField).collidepoint(mouse_pos):
                return row,column
    return -1,-1

def CheckGameEnd(BoardState):
    global chess_active
    global ToMove
    if not chessCore.IsMate(BoardState) == "": print(f"Mate: {chessCore.IsMate(BoardState)}")
    if not chessCore.IsStaleMate(BoardState) == "": print(f"Stale Mate: {chessCore.IsStaleMate(BoardState)}")    
    # chess_active = False
    BoardState, ToMove = chessCore.Readfen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    return BoardState

def HandelMove(start,end,ToMove):
    global FullMove
    global HalfMove
    global BoardState
    global Capture

    HalfMove += 1
    #Logic if a valid move is performed
    BoardState, Capture = chessCore.MakeMove(BoardState,start,end)
    if chessCore.GetPieceType(BoardState[end[0]][end[1]]) == "P": HalfMove = 0
    if Capture > 0: HalfMove = 0
    DisplayBoardState = copy.deepcopy(BoardState)  # fresh copy for display
    valid_moves = []

    
    if ToMove != FirstMove:FullMove += 1 #incremtt every second move
    ToMove = "b" if ToMove == "w" else "w"
    print(f"Current Position: {chessCore.CreateFen(BoardState,ToMove,Halfmove=HalfMove,Fullmove=FullMove)}")

    return valid_moves,DisplayBoardState,ToMove


chess_active = True
PieceMasks = CreatePieceMasks()

piecepickedup = -1
start_square = (-1,-1)
valid_moves = []

#set initial starting postion
BoardState, ToMove = chessCore.Readfen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
FirstMove = ToMove
DisplayBoardState = copy.deepcopy(BoardState)

FullMove = 0
HalfMove = 0

print(ToMove)

WAIT_TIME = 0 # 1 second in milliseconds
last_move_time = 0
move_in_progress = False

NOAI = False
PLAYER_AGAINST_AI = True

while chess_active:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            chess_active = False

        elif event.type == pygame.MOUSEBUTTONDOWN and piecepickedup == -1:
            clicked_row, clicked_col = CheckFieldClicked(mouse_pos)
            piece = BoardState[clicked_row][clicked_col]
            if piece > 0 and chessCore.GetPieceColor(piece) == ToMove:
                piecepickedup = piece
                start_square = (clicked_row, clicked_col)
                DisplayBoardState[clicked_row][clicked_col] = 0
                valid_moves = chessCore.ValidPieceMoves(BoardState, start_square, piece, ToMove)

        elif event.type == pygame.MOUSEBUTTONUP and piecepickedup > -1:
            clicked_row, clicked_col = CheckFieldClicked(mouse_pos)
            if (clicked_row, clicked_col) in valid_moves:
                valid_moves, DisplayBoardState, ToMove = HandelMove(start_square, (clicked_row, clicked_col), ToMove)
                last_move_time = pygame.time.get_ticks()  # record when the move happened
                move_in_progress = True
            else:
                DisplayBoardState[start_square[0]][start_square[1]] = piecepickedup
                valid_moves = []
            piecepickedup = -1
            start_square = (-1, -1)

    # AI moves — only if enough time has passed
    if move_in_progress and pygame.time.get_ticks() - last_move_time < WAIT_TIME or NOAI:
        # waiting — skip move
        pass
    else:
        if ToMove == FirstMove:
            valid_moves = chessCore.ValidMoves(BoardState, ToMove)
            if len(valid_moves) == 0: BoardState = CheckGameEnd(BoardState)
            else:
                start_square, end_square = chessAI.Simple_AI.Move(BoardState, ToMove, valid_moves)
                valid_moves, DisplayBoardState, ToMove = HandelMove(start_square, end_square, ToMove)
                last_move_time = pygame.time.get_ticks()
                move_in_progress = True

        elif ToMove != FirstMove and not PLAYER_AGAINST_AI:
            valid_moves = chessCore.ValidMoves(BoardState, ToMove)

            if len(valid_moves) == 0: BoardState = CheckGameEnd(BoardState)
            else:
                start_square, end_square = chessAI.Random_Ai.Move(BoardState, ToMove, valid_moves)
                valid_moves, DisplayBoardState, ToMove = HandelMove(start_square, end_square, ToMove)
                last_move_time = pygame.time.get_ticks()
    #             move_in_progress = True
    if HalfMove > 50:
        print("50 Half Moves DRAW")
        # chess_active = False
        BoardState, ToMove = chessCore.Readfen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    screen.fill((125, 125, 125))
    DrawBoard(screen)
    DrawValidMoves(screen, valid_moves)
    DrawPieces(screen, DisplayBoardState, mouse_pos)
    pygame.display.flip()
  #  clock.tick(60)





pygame.quit()