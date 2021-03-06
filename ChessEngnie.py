#Stores information of current state of the game
#Checks for valid moves in current state
#Keeps Move log

class GameState():
    def __init__(self):
        # 2D list to make board
        #fisrt letter is the color and the second letter is the type
        #-- is an empty space
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
            ]

        self.moveFunctions = {'P':self.getPawnMoves, 'R':self.getRookMoves, 'N':self.getKnightMoves,
                              'B':self.getBishopMoves, 'Q':self.getQueenMoves, 'K':self.getKingMoves}
        self.whiteTurn = True
        self.moveLog = []

        #see if king is in check
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = ()
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)
        #change turns
        self.whiteTurn = not self.whiteTurn
        #keep track of king
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        
        #pawn promotaion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'

        #update enpassant
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = '--' #erase old rook
            else: #queen side castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]
                self.board[move.endRow][move.endCol -2] = '--'

        #update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                            self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))


    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False

    #moves looks for checks
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        moves = self.getAllMoves()
        
        for i in range(len(moves)-1,-1,-1):#when removing from list go backwards
            self.makeMove(moves[i])

            self.whiteTurn = not self.whiteTurn #change turns
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteTurn = not self.whiteTurn #change turns again

        if len(moves) == 0: #checks stale mate
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True

        if self.whiteTurn:
            self.getCastleMoves(self.whiteKingLocation[0],self.whiteKingLocation[1],moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0],self.blackKingLocation[1],moves)

        self.enpassantPossible = tempEnpassantPossible   
        self.currentCastlingRight = tempCastleRights

        return moves

    #checks for current turn is in check
    def inCheck(self):
        if self.whiteTurn:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    #can enemy attack the square 
    def squareUnderAttack(self,r,c):
        self.whiteTurn = not self.whiteTurn #get opponents pov
        oppMoves = self.getAllMoves()
        self.whiteTurn = not self.whiteTurn #change pov
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #square is getting attacked
                return True
        return False

    #legal moves
    def getAllMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteTurn) or (turn == 'b' and not self.whiteTurn):
                    piece = self.board[r][c][1]
                    #uses dictionary to mark valid moves for each piece
                    self.moveFunctions[piece](r,c,moves)
        return moves

    #pawn legal moves
    def getPawnMoves(self, r, c, moves):
        if self.whiteTurn:
            if self.board[r-1][c] == "--":
                moves.append(Move((r,c),(r-1,c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r,c), (r-2,c), self.board))
            #getting enemy piece while white pawn
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r,c), (r-1,c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r-1,c-1), self.board, isEnpassantMove = True))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c),(r-1,c+1),self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r-1,c+1), self.board, isEnpassantMove = True))
        #black pawn
        else:
            if self.board[r+1][c] == "--":
                moves.append(Move((r,c),(r+1,c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r,c),(r+2,c), self.board))
            #getting white pawn
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r,c), (r+1,c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r+1,c-1), self.board, isEnpassantMove = True))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c),(r+1,c+1),self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r,c), (r+1,c+1), self.board, isEnpassantMove = True))
  
    #Rook legal Moves   
    def getRookMoves(self,r,c, moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1)) #up left down right
        enemyColor = "b" if self.whiteTurn else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c),(endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    #freidnly piece invalid
                    else:
                        break
                #off board
                else:
                    break

    #Knight legal Moves
    def getKnightMoves(self,r,c, moves):
        knightMoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        allyColor = "w" if self.whiteTurn else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                        moves.append(Move((r,c),(endRow, endCol), self.board))

    #Bishop legal Moves
    def getBishopMoves(self,r,c, moves):
        directions = ((-1,-1),(-1,1),(1,-1),(1,1)) #4 diagonals
        enemyColor = "b" if self.whiteTurn else "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r,c),(endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c),(endRow,endCol),self.board))
                        break
                    #freidnly piece invalid
                    else:
                        break
                #off board
                else:
                    break

    #Queen legal Moves
    def getQueenMoves(self,r,c, moves):
        self.getBishopMoves(r,c, moves)
        self.getRookMoves(r,c, moves)

    #King legal Moves
    def getKingMoves(self,r,c, moves):
        directions = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        allyColor = "w" if self.whiteTurn else "b"
        for i in range(8):
            endRow = r + directions[i][0]
            endCol = c + directions[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r,c), (endRow,endCol), self.board))


    #generates possible castle moves for king
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r,c):
            return #cant castle in check
        if (self.whiteTurn and self.currentCastlingRight.wks) or (not self.whiteTurn and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r,c,moves)
        if (self.whiteTurn and self.currentCastlingRight.wqs) or (not self.whiteTurn and self.currentCastlingRight.bqs):
            self.getQueensidesCastleMoves(r,c,moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if (not self.squareUnderAttack(r,c+1)) and (not self.squareUnderAttack(r,c+2)):
                moves.append(Move((r,c),(r,c+2), self.board, isCastleMove=True))

    def getQueensidesCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3]:
             if (not self.squareUnderAttack(r,c-1)) and (not self.squareUnderAttack(r,c-2)):
                moves.append(Move((r,c),(r,c-2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    #key to values
    #key : value
    ranksToRows = {"1" : 7, "2":6, "3":5, "4":4, "5":3, "6":2, "7":1, "8":0 }
    rowsToRanks = {v:k for k, v in ranksToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'
        #castle move
        self.isCastleMove = isCastleMove
 
        self.moveID = self.startRow * 1000 + self.startCol * 100 +self.endRow * 10 + self.endCol

    #override the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]