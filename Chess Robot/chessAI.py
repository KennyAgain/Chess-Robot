import random
import copy
import chessCore


class Random_Ai:
    def Move(BoardState,ToMove,ValidMoves):

        Move = ValidMoves[random.randint(0,len(ValidMoves) - 1)]

        print(f"AI Move {Move}")

        Startsquare = Move[0]
        Endsquare = Move[1]

        return Startsquare, Endsquare
    
class Simple_AI:
    
    @staticmethod
    def Eval(BoardState, ToMove, Capture):
        MaterialCounter = 0
        CapturePenalty = 0
        
        Mate = chessCore.IsMate(BoardState)
        if Mate == ToMove: return -9999
        elif not Mate == "": return 9999

        for row in BoardState:
            for piece in row:
                if piece != 0:
                    if chessCore.GetPieceColor(piece) == ToMove:
                        MaterialCounter += chessCore.MaterialValue[piece]
                    else:
                        MaterialCounter -= chessCore.MaterialValue[piece]

        # Apply capture bonus/penalty
        if Capture != 0:
            if chessCore.GetPieceColor(Capture) == ToMove:
                CapturePenalty -= chessCore.MaterialValue[Capture] * 1.5
            else:
                CapturePenalty += chessCore.MaterialValue[Capture] * 1.5

        FinalEval = MaterialCounter + CapturePenalty
        return FinalEval

    @staticmethod
    def Move(BoardState, ToMove, ValidMoves,depth=2):
        BestEval = -99999
        BestEvalIndex = 0

        for index, Move in enumerate(ValidMoves):
            MockBoard = copy.deepcopy(BoardState)
            MockBoard, Capture = chessCore.MakeMove(MockBoard, Move[0], Move[1])

            MoveEvaluation = Simple_AI.Eval(MockBoard, ToMove, Capture)

            if MoveEvaluation > BestEval:
                BestEval = MoveEvaluation
                BestEvalIndex = index

        BestMove = ValidMoves[BestEvalIndex]
        print(f"AI Move {BestMove}")

        Startsquare = BestMove[0]
        Endsquare = BestMove[1]
        return Startsquare, Endsquare

        

        