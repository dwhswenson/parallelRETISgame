import numpy as np
import random
import copy
from collections import namedtuple

MoveReport = namedtuple('MoveReport', 'move node')

class Move(object):
    def __init__(self, cost_function, depends_on):
        self.cost_function = cost_function
        self.depends_on = depends_on

    def cost(self):
        return self.cost_function()

class FastCost(object):
    def __call__(self):
        return 1

class ShootingCost(object):
    def __init__(self, mean, dev, skew):

        pass

    def __call__(self):
        return 10

class ShootingMove(Move):
    def __repr__(self):
        return "Shooting" + str(self.depends_on[0])

class ReplicaExchangeMove(Move):
    def __init__(self, repA, repB):
        super(ReplicaExchangeMove, self).__init__(FastCost(), [repA, repB])

    def __repr__(self):
        return "Repex" + str(self.depends_on)


class DefaultStrategy(object):
    @staticmethod
    def available_nodes(status):
        return [i for i in range(len(status)) if status[i] is None]

    def update(self, legal_moves, status, time):
        nodes = self.available_nodes(status)
        moves = [MoveReport(move=legal_moves[i], node=nodes[i])
                 for i in range(min(len(nodes), len(legal_moves)))]
        # print moves
        return moves


class Game(object):
    def __init__(self, moves, strategy, n_nodes):
        self.moves = moves
        self.strategy = strategy
        self.n_nodes = n_nodes
        self.history = [list([]) for i in range(self.n_nodes)]

    def assign_move_to_node(self, move, node):
        cost = move.cost()
        self.history[node] += [move]*cost

    @staticmethod
    def ensemble_history(history, replica):
        pass

    def verify(self):
        # check that history and serial history give the same behavior for
        # each ensemble
        pass

    @staticmethod
    def legal_moves(status, move_list):
        active = sum([move.depends_on for move in status 
                      if move is not None], [])
        legal_moves = []
        for move in move_list:
            if list(set(move.depends_on) & set(active)) == []:
                legal_moves.append(move)
                active.extend(move.depends_on)
        return legal_moves

    def status(self, time):
        status = [None] * self.n_nodes
        for node_i in range(self.n_nodes):
            try:
                status[node_i] = self.history[node_i][time]
            except IndexError:
                pass
        return status

    @staticmethod
    def analysis(history):
        n_nodes = len(history)
        wall_time = max([len(node) for node in history])
        cpu_time = wall_time * n_nodes
        wasted_cycles = 0
        for node in history:
            wasted_cycles += len([act for act in node if act is None])
        print "Wall time:", wall_time
        print "CPU time:", cpu_time
        print "Wasted cycles:", wasted_cycles
        print "Efficiency:", float(cpu_time-wasted_cycles) / cpu_time


    def play(self, n_steps):
        move_queue = [random.choice(self.moves) for i in range(n_steps)]
        play_queue = copy.copy(move_queue)
        # TODO: run the correct version of the move queue
        t = 0
        while play_queue != [] or self.status(t) != [None] * self.n_nodes:
            status = self.status(t)
            legal_moves = self.legal_moves(status, play_queue)

            moves = self.strategy.update(legal_moves, status, t)
            if not isinstance(moves, list):
                moves = [moves]
            for move in moves:
                self.assign_move_to_node(move.move, move.node)
                play_queue.remove(move.move)

            status = self.status(t)
            empty_nodes = [i for i in range(len(status)) if status[i] is None]
            for node_i in empty_nodes:
                self.history[node_i].append(None)

            # print t, self.status(t)
            t += 1

        pass
