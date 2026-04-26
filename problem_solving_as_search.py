"""
Implement both the best-first and the A* search algorithms 
to search for a solution to the 8-puzzle, as described in the textbook. 
The input to your program should be a configuration of the 8 puzzle, e.g,

(4 5 b) 
(6 1 8)
(7 3 2) 

(where b = “blank”) corresponds to:

The goal state is 

(1 2 3) 
(4 5 6) 
(7 8 b)

Implement three different heuristics—the two described 
in the textbook plus one of your own devising—for evaluating 
states in the state space. 

Run your search algorithms (stopping it after some maximum number 
of steps if the solution is not found) using each of these three heuristics
on each of five different initial states. Your program should output the solution path it found (if
one was found), e.g,

(4 5 b) 
(6 1 8) 
(7 3 2) 
→ 
(4 b 5) 
(6 1 8)
(7 3 2) 
→ 
… 
→ 
(1 2 3) 
(4 5 6) 
(7 8 b)

In your write-up, describe the three heuristics, and, for each of the heuristics, 
give the solution path discovered for each initial state, and the 
average number of steps in the path over the five
trials.

Extra credit (+10%): Produce the same data for the 15-puzzle 
(you don’t need to give the actual solution paths, just the average 
number of steps for each heuristic).

"""

class Problem:
    def __init__(self):
        self.board_config = [4, 5, "b", 6, 1, 8, 7, 3, 2]
        self.goal_board_config = [1, 2, 3, 4, 5, 6, 7, 8, "b"]
        self.idea_board_config = [1,2,3,4,5,6,7,8,"b"]

    def my_print(self):
        print(self.goal_board_config)
        print(self.board_config)

