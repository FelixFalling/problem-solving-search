# -------------------------------------------------------
# Goal state and initial states
# -------------------------------------------------------

GOAL = (1, 2, 3, 4, 5, 6, 7, 8, "b")

INITIAL_STATES = [
    [4, 5, "b", 6, 1, 8, 7, 3, 2], 
    [1, 2, 3, 4, "b", 5, 7, 8, 6],
    [1, 2, 3, 7, 4, 5, "b", 8, 6],
    [4, 1, 3, 7, 2, 5, "b", 8, 6],
    [1, 6, 2, 5, 3, "b", 4, 7, 8],
    [8, 6, 7, 2, 5, 4, 3, "b", 1],
]


# -------------------------------------------------------
# Puzzle state
# -------------------------------------------------------

class PuzzleState:
    def __init__(self, board, parent=None, g=0):
        self.board = tuple(board)
        self.parent = parent
        self.g = g
        self.blank_pos = self.board.index("b")

    def get_successors(self):
        successors = []
        row, col = divmod(self.blank_pos, 3)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                new_pos = nr * 3 + nc
                board = list(self.board)
                board[self.blank_pos], board[new_pos] = board[new_pos], board[self.blank_pos]
                successors.append(PuzzleState(board, self, self.g + 1))
        return successors

    def is_goal(self):
        return self.board == GOAL

    def get_solution_path(self):
        path, state = [], self
        while state is not None:
            path.append(state.board)
            state = state.parent
        return list(reversed(path))

    def __hash__(self):
        return hash(self.board)

    def __eq__(self, other):
        return self.board == other.board


# -------------------------------------------------------
# Heuristic 1 — Misplaced tiles 
# Count how many tiles are not in their goal position.
# -------------------------------------------------------

def h_misplaced_tiles(state):
    return sum(1 for i, t in enumerate(state.board) if t != "b" and t != GOAL[i])


# -------------------------------------------------------
# Heuristic 2 — Manhattan distance 
# Sum of how far each tile is from its goal position.
# -------------------------------------------------------

GOAL_POS = {t: divmod(i, 3) for i, t in enumerate(GOAL)}

def h_manhattan_distance(state):
    total = 0
    for i, t in enumerate(state.board):
        if t != "b":
            r, c = divmod(i, 3)
            gr, gc = GOAL_POS[t]
            total += abs(r - gr) + abs(c - gc)
    return total


# -------------------------------------------------------
# Heuristic 3 — Linear conflict (custom)
# Manhattan distance + 2 for each tile that must leave
# its goal row/column because another tile is blocking it.
# -------------------------------------------------------

def _min_removals_for_line(tiles):
    n = len(tiles)
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            ci, gi = tiles[i]
            cj, gj = tiles[j]
            if (ci < cj) != (gi < gj):
                adj[i].append(j)
                adj[j].append(i)
    removed = [False] * n
    count = 0
    while True:
        best, best_idx = 0, -1
        for i in range(n):
            if not removed[i]:
                c = sum(1 for j in adj[i] if not removed[j])
                if c > best:
                    best, best_idx = c, i
        if best == 0:
            break
        removed[best_idx] = True
        count += 1
    return count

def h_linear_conflict(state):
    base = h_manhattan_distance(state)
    extra = 0
    for row in range(3):
        tiles = [(col, GOAL_POS[state.board[row * 3 + col]][1])
                 for col in range(3)
                 if state.board[row * 3 + col] != "b"
                 and GOAL_POS[state.board[row * 3 + col]][0] == row]
        extra += _min_removals_for_line(tiles)
    for col in range(3):
        tiles = [(row, GOAL_POS[state.board[row * 3 + col]][0])
                 for row in range(3)
                 if state.board[row * 3 + col] != "b"
                 and GOAL_POS[state.board[row * 3 + col]][1] == col]
        extra += _min_removals_for_line(tiles)
    return base + 2 * extra


# -------------------------------------------------------
# Search algorithms
# -------------------------------------------------------

def _pop_min(frontier):
    min_idx = 0
    for i in range(1, len(frontier)):
        if frontier[i][0] < frontier[min_idx][0]:
            min_idx = i
    return frontier.pop(min_idx)

def best_first_search(initial_board, heuristic, max_steps=200_000):
    start = PuzzleState(initial_board)
    if start.is_goal():
        return start.get_solution_path(), 0
    frontier = [(heuristic(start), start)]
    visited  = {start.board}
    steps    = 0
    while frontier and steps < max_steps:
        _, state = _pop_min(frontier)
        steps += 1
        for s in state.get_successors():
            if s.board not in visited:
                if s.is_goal():
                    return s.get_solution_path(), steps
                visited.add(s.board)
                frontier.append((heuristic(s), s))
    return None, steps

def astar_search(initial_board, heuristic, max_steps=200_000):
    start = PuzzleState(initial_board)
    if start.is_goal():
        return start.get_solution_path(), 0
    frontier = [(heuristic(start), start)]
    best_g   = {start.board: 0}
    steps    = 0
    while frontier and steps < max_steps:
        _, state = _pop_min(frontier)
        steps += 1
        if state.is_goal():
            return state.get_solution_path(), steps
        if state.g > best_g.get(state.board, float("inf")):
            continue
        for s in state.get_successors():
            ng = state.g + 1
            if ng < best_g.get(s.board, float("inf")):
                best_g[s.board] = ng
                s.g = ng
                frontier.append((ng + heuristic(s), s))
    return None, steps


# -------------------------------------------------------
# Run experiments
# -------------------------------------------------------

def is_solvable(board):
    tiles = [t for t in board if t != "b"]
    inversions = sum(
        1 for i in range(len(tiles))
        for j in range(i + 1, len(tiles))
        if tiles[i] > tiles[j]
    )
    return inversions % 2 == 0

def run_experiments(verbose=True):
    heuristics = [
        ("Heuristic 1 (Misplaced Tiles)",    h_misplaced_tiles),
        ("Heuristic 2 (Manhattan Distance)", h_manhattan_distance),
        ("Heuristic 3 (Linear Conflict)",    h_linear_conflict),
    ]
    algorithms = [
        ("Best-first search", best_first_search),
        ("A* search",         astar_search),
    ]
    for algo_name, algo in algorithms:
        print(algo_name)
        for h_name, h_func in heuristics:
            print(h_name)
            step_counts = []
            for state in INITIAL_STATES:
                if not is_solvable(state):
                    print(" ".join(str(t) for t in state), "is not solvable, skipping")
                    continue
                path, _ = algo(state, h_func)
                if path is not None:
                    step_counts.append(len(path) - 1)
                    if verbose:
                        print(" -> ".join("(" + " ".join(str(t) for t in b) + ")" for b in path))
                else:
                    print(" ".join(str(t) for t in state), "no solution found")
            if step_counts:
                print("Average number of steps:", sum(step_counts) / len(step_counts))
            print()
