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
    def Eval(BoardState):
        """Evaluation from White's perspective (+ good for White, - good for Black)."""
        score = 0
        for row in BoardState:
            for piece in row:
                if piece != 0:
                    val = chessCore.MaterialValue[piece]
                    if chessCore.GetPieceColor(piece) == "w":
                        score += val
                    else:
                        score -= val
        return score

    @staticmethod
    def quick_move_score(move, BoardState, ToMove):
        (sx, sy), (ex, ey) = move
        attacker = BoardState[sx][sy]
        victim   = BoardState[ex][ey]

        # Base score = 0 (quiet move)
        score = 0

        if victim != 0:
            # MVV-LVA: prefer capturing the most valuable victim with the least valuable attacker
            score = (chessCore.MaterialValue[victim] * 10) - chessCore.MaterialValue[attacker]

        # if move_results_in_check(BoardState, move, ToMove):
        #     score += 50

        return score



    @staticmethod
    def Move(BoardState, ToMove, ValidMoves, depth=3):
        eval, BestEvalIndex = Simple_AI.Search(BoardState, ToMove, ValidMoves, depth, -999999, 999999)
        print(f"Best Eval {eval}")
        BestMove = ValidMoves[BestEvalIndex]
        print(f"AI Move {BestMove}")
        return BestMove[0], BestMove[1]

    @staticmethod
    def Search(BoardState, ToMove, ValidMoves, depth, alpha, beta):
        if depth == 0 or not ValidMoves:
            return Simple_AI.Eval(BoardState), None

        BestEval = -99999 if ToMove == "w" else 99999
        BestEvalIndex = 0

        ValidMoves.sort(key=lambda m: Simple_AI.quick_move_score(m, BoardState, ToMove), reverse=True) #move ordering
        for index, Move in enumerate(ValidMoves):
            MockBoard = copy.deepcopy(BoardState)
            MockBoard, Capture = chessCore.MakeMove(MockBoard, Move[0], Move[1])

            next_color = "b" if ToMove == "w" else "w"
            next_moves = chessCore.ValidMoves(MockBoard, next_color)
            score, _ = Simple_AI.Search(MockBoard, next_color, next_moves, depth-1, alpha, beta)

            if ToMove == "w":  # maximizing
                if score > BestEval:
                    BestEval = score
                    BestEvalIndex = index

                alpha = max(alpha, BestEval)
                if alpha >= beta:
                    break
            else:  # minimizing
                if score < BestEval:
                    BestEval = score
                    BestEvalIndex = index

                beta = min(beta, BestEval)
                if alpha >= beta:
                    break

        return BestEval, BestEvalIndex



            

        

        