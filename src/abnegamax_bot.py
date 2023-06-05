#   ____        _            _              _   ____                     
#  |  _ \  ___ | |_ ___     / \   _ __   __| | | __ )  _____  _____  ___ 
#  | | | |/ _ \| __/ __|   / _ \ | '_ \ / _` | |  _ \ / _ \ \/ / _ \/ __|
#  | |_| | (_) | |_\__ \  / ___ \| | | | (_| | | |_) | (_) >  <  __/\__ \
#  |____/ \___/ \__|___/ /_/   \_\_| |_|\__,_| |____/ \___/_/\_\___||___/                                                                                
#
###############################
##CS4386 Semester B, 2019-2020#
##Assignment 2                #
##Name: Zhang Deheng          #
##Student ID: 55199998        #
###############################

botName='4386_20B_9998-defbot'
import random
import json
import copy
import time
import numpy as np
import pandas as pd

# a large number to represent the infinity
INFINITY = 100000000000
# Turn off the randomization of the best move, choose the first move
RANDOMIZE = False
def from_list_to_dict(gamestate):
    gamedict = {}
    gamedict['Dimensions'] = gamestate['Dimensions']
    gamedict['IsMover'] = gamestate['IsMover']
    gamedict['ResponseDeadline'] = gamestate['ResponseDeadline']
    gamedict['MyScore'] = gamestate['MyScore']
    gamedict['OppScore'] = gamestate['OppScore'] 
    gamedict['InvalidMove'] = gamestate['InvalidMove']
    gamedict['OpponentId'] = gamestate['OpponentId']
    gamedict['GameStatus'] = gamestate['GameStatus']
    gamedict['Grid'] = {}
    gamedict['Squares'] = []
    
    for line in gamestate['Grid']:
        move = (line[0], line[1])
        gamedict['Grid'][str(move)] = line
        
    for square in gamestate['Squares']:
        lines_already_complete = list(filter(lambda l: l[2], square[0]))
        num_lines_complete = len(lines_already_complete)
        gamedict['Squares'].append(num_lines_complete)
        
    return gamedict

class Board:
    def __init__(self, gamestate):
        # change the data structure of the gamestate to the dictionary
        self.state = gamestate
        self.dimensions = gamestate['Dimensions']
        self.is_mover = gamestate['IsMover']
        self.res_ddl = gamestate['ResponseDeadline']
        self.my_score = gamestate['MyScore']
        self.opp_score = gamestate['OppScore'] 
        self.game_status = gamestate['GameStatus']
        self.grid = gamestate['Grid']
        self.squares = gamestate['Squares']

    def finished(self):
        return self.game_status == 'STOPPED'

    def isMover(self):
        return self.is_mover

    def take_move(self, move):
        # take move according to the current game state
        m = self.dimensions[0]; n = self.dimensions[1]
        gamesize = (m-1)*(n-1)
        gamestate_sim = json.loads(json.dumps(self.state))
        
        # update grid
        gamestate_sim['Grid'][str((move[0], move[1]))][2] = 0 if gamestate_sim['IsMover'] else 1
        
        # update square
        (x, y) = move
        score = 0
        squares = gamestate_sim['Squares']
        if x[0] == y[0]:
            if not x[0] == 0:
                idx = (n-1)*(x[0]-1)+x[1]
                squares[idx] += 1
                if squares[idx] == 4:
                    score = score + 1
            if not x[0] == (m-1):
                idx = (n-1)*x[0]+x[1]
                squares[idx] += 1
                if squares[idx] == 4:
                    score = score + 1
        elif x[1] == y[1]:
            if not x[1] == 0:
                idx = (n-1)*x[0]+(x[1]-1)
                squares[idx] += 1
                if squares[idx] == 4:
                    score = score + 1
            if not x[1] == (n-1):
                idx = (n-1)*x[0]+x[1]
                squares[idx] += 1
                if squares[idx] == 4:
                    score = score + 1

        # update score
        if gamestate_sim['IsMover']:
            gamestate_sim['MyScore'] += score
        else:
            gamestate_sim['OppScore'] += score
            
        # update GameStatus
        if gamestate_sim['MyScore'] > gamesize/2 or gamestate_sim['OppScore'] > gamesize/2 or gamestate_sim['OppScore']+gamestate_sim['MyScore']==gamesize:
            gamestate_sim['GameStatus'] = 'STOPPED'
        
        # update IsMover
        gamestate_sim['IsMover'] = gamestate_sim['IsMover'] if score > 0 else( not gamestate_sim['IsMover'])
        
        return Board(gamestate_sim)

    def take_move_chain(self, maxDepth):
        # take a chain of moves as long as there are completable squares
        m = self.dimensions[0]; n = self.dimensions[1]
        current_board = self
        completable_squares = [i for i, square in enumerate(current_board.squares) if square == 3]
        if len(completable_squares) == 0:
            return current_board
        
        currentDepth = 0
        while len(completable_squares) > 0 and currentDepth < maxDepth and (not current_board.finished()):
            currentDepth += 1
            idx = random.randint(0, len(completable_squares)-1)
            x = completable_squares[idx] // (n-1)
            y = completable_squares[idx] % (n-1)
            line1 = ([x, y], [x + 1, y])
            line2 = ([x, y], [x, y + 1])
            line3 = ([x + 1, y], [x + 1, y + 1])
            line4 = ([x, y + 1], [x + 1, y + 1])

            grid = current_board.grid
            if grid[str(line1)][2] == -1 :
                current_board = current_board.take_move(line1)
            elif grid[str(line2)][2] == -1 :
                current_board = current_board.take_move(line2)
            elif grid[str(line3)][2] == -1 :
                current_board = current_board.take_move(line3)
            elif grid[str(line4)][2] == -1 :
                current_board = current_board.take_move(line4)
            
            completable_squares = [i for i, square in enumerate(current_board.squares) if square == 3]
            num_completable_squaresd = len(completable_squares)
        return current_board
    
    def get_legal_moves(self):
        # return a list of legal moves
        legal_moves = []
        for key in self.grid:
            if self.grid[key][2] == -1: # then neither player has made this move
                legal_moves.append([ self.grid[key][0],  self.grid[key][1]])
        return legal_moves

    def take_random_move(self):
        # take random move according to the current gamestate
        legal_moves = self.get_legal_moves()
        x = random.randint(0, len(legal_moves)-1)
        return self.take_move(legal_moves[x])

    def evaluate(self):
        score = self.my_score - self.opp_score
        return (score if self.is_mover else -score)

    def evaluate_1(self):
        # Heuristic evaluation based on the current state and number of completable squares

        current_score = self.evaluate()

        # Chain Cases
        completable_squares = list(filter(lambda square: square == 3, self.squares))
        num_completable_squares = len(completable_squares)
        score = current_score + num_completable_squares
        return score

    def evaluate_2(self):
        # Heuristic evaluation based on simulation
        # There will be a chain of simulation until the player is changed (i.e. 0 score exists)
        return (self.take_move_chain(40)).evaluate()

# main algorithm
def abnegamax(board, maxDepth, currentDepth, alpha, beta):
    if board.finished() or (maxDepth == currentDepth) :
        score = board.evaluate_2()
        return score, None
    
    bestMove = []
    bestScore = -INFINITY
    
    legal_moves = board.get_legal_moves()
    for move in legal_moves:
        newBoard = board.take_move(move)
        recursedScore = 0 
        currentScore = 0
        currentMove = None

        # calculate the bestscore for the newstate and store
        if board.isMover() == newBoard.isMover():
            (recursedScore, currentMove) = abnegamax(newBoard, maxDepth, currentDepth+1, max(alpha, bestScore), beta)
            currentScore = recursedScore
        else:
            (recursedScore, currentMove) = abnegamax(newBoard, maxDepth, currentDepth+1, -beta, -max(alpha, bestScore))
            currentScore = -recursedScore
            
        # Update the best score
        if currentScore > bestScore:
            bestScore = currentScore
            bestMove = []
            bestMove.append(move)
                
        # If we're outside the bounds, then prune: exit immediately
        if bestScore >= beta:
            return bestScore, bestMove
            
        # store all the moves with the same score
        if currentScore == bestScore:
            bestMove.append(move)
        
        
    return bestScore, bestMove

# function will be called
def calculate_move(gamestate):
    gamestate = from_list_to_dict(gamestate)
    board = Board(gamestate)
    # empty the transposition table
    (bestScore, bestMoves) = abnegamax(board, 2, 0, -INFINITY, INFINITY)
    idx = random.randint(0, len(bestMove) - 1) if RANDOMIZE == True else 0
    # print('deadline: ' + str(board['ResponseDeadline']))
    # print('finish: ' + str(time.time()))
    return bestMoves[idx]
