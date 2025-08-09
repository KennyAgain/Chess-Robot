import pygame
import chessAI
import chessCore

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


piece_Image = pygame.image.load("pieces.png").convert_alpha()
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

#set initial starting postion
BoardPieces = chessCore.Readfen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR")

while chess_active:

    for event in pygame.event.get():
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.QUIT:
            chess_active = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if piecepickedup == -1:
                
                clicked_row, clicked_column = CheckFieldClicked(mouse_pos)

                if BoardPieces[clicked_row][clicked_column] > 0:
                    piecepickedup = BoardPieces[clicked_row][clicked_column]
                    BoardPieces[clicked_row][clicked_column] = 0

        if event.type == pygame.MOUSEBUTTONUP:
            if piecepickedup > -1:
                clicked_row, clicked_column = CheckFieldClicked(mouse_pos)
                BoardPieces[clicked_row][clicked_column] = piecepickedup
                piecepickedup = -1
                print(mouse_pos)
 

    screen.fill((125,125,125))

    DrawBoard(screen)
    DrawPieces(screen,BoardPieces,mouse_pos)

    pygame.display.flip()

    clock.tick(60)




pygame.quit()