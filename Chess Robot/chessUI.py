import pygame
import chessAI
import chessCore
import chessRobotCom
import copy

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
    
    if piecepickedup > -1:
        screen.blit(piece_Image,(mouse_pos[0] - stepPerField/2,mouse_pos[1] - stepPerField/2),PieceMasks[piecepickedup - 1])

def CheckFieldClicked(mouse_pos):
    stepPerField = H / 8
    for row in range(8):
        for column in range(8):
            if pygame.Rect(row*stepPerField,column*stepPerField,stepPerField,stepPerField).collidepoint(mouse_pos):
                return row,column

chess_active = True
PieceMasks = CreatePieceMasks()

piecepickedup = -1
start_square = (-1,-1)

#set initial starting postion
BoardState = chessCore.Readfen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")
DisplayBoardState = copy.deepcopy(BoardState)

while chess_active:

    for event in pygame.event.get():
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.QUIT:
            chess_active = False

        elif event.type == pygame.MOUSEBUTTONDOWN and piecepickedup == -1:
            clicked_row, clicked_col = CheckFieldClicked(mouse_pos)

            piece = BoardState[clicked_row][clicked_col]
            if piece > 0:
                piecepickedup = piece
                start_square = (clicked_row, clicked_col)
                # Remove from display state only
                DisplayBoardState[clicked_row][clicked_col] = 0

        elif event.type == pygame.MOUSEBUTTONUP and piecepickedup > -1:
            clicked_row, clicked_col = CheckFieldClicked(mouse_pos)
            valid_moves = chessCore.ValidMoves(BoardState, start_square)

            if (clicked_row, clicked_col) in valid_moves:
                BoardState[clicked_row][clicked_col] = piecepickedup
                BoardState[start_square[0]][start_square[1]] = 0
                DisplayBoardState = copy.deepcopy(BoardState)  # fresh copy for display
            else:
                # Invalid move: restore piece in display state for smooth visual
                DisplayBoardState[start_square[0]][start_square[1]] = piecepickedup

            piecepickedup = -1
            start_square = (-1, -1)


    screen.fill((125,125,125))

    DrawBoard(screen)
    DrawPieces(screen,DisplayBoardState,mouse_pos)

    pygame.display.flip()

    clock.tick(60)




pygame.quit()