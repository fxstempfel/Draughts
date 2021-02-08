from typing import List, Optional, Set


class Color:
    BLACK = "black"
    WHITE = "white"

    def __init__(self, color):
        self.color = color

    def opponent(self):
        if self.color == self.BLACK:
            return self.WHITE
        else:
            return self.BLACK

    def move_is_forward(self, current_cell, target_cell):
        is_positive = target_cell.y - current_cell.y > 0
        if is_positive and self.color == self.WHITE or not is_positive and self.color == self.BLACK:
            return True
        else:
            return False


class Cell:
    def __init__(self, x, y):
        self.position = x, y
        self.x = x
        self.y = y

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return f"Cell({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def neighbors(self):
        terms_i = 1, -1, 1, -1
        terms_j = 1, 1, -1, -1
        neighbors = [Cell(self.x + i, self.y + j) for i, j in zip(terms_i, terms_j)]
        return [n for n in neighbors if n.is_within_board()]

    def is_within_board(self):
        return 0 <= self.x <= 9 and 0 <= self.y <= 9

    def get_next_in_direction(self, other):
        direction_x = other.x - self.x
        direction_y = other.y - self.y
        next_cell = Cell(other.x + direction_x, other.y + direction_y)
        if next_cell.is_within_board():
            return next_cell
        else:
            return None


class Move:
    def __init__(self, moved_to: Cell):
        self.moved_to = moved_to


class Take(Move):
    def __init__(self, moved_to: Cell, taken: Cell):
        super().__init__(moved_to)
        self.taken = taken
        self.moved_to = moved_to

    def __repr__(self):
        return f"Take({self.moved_to} by {self.taken})"


class PossibleTakes:
    def __init__(self, takes: List[Take]):
        self.list_of_takes_series = [takes]

    def __len__(self):
        return len(self.list_of_takes_series)

    def __repr__(self):
        return f"PossibleTakes({self.list_of_takes_series})"

    def longest_size(self):
        try:
            return max(len(l) for l in self.list_of_takes_series)
        except ValueError:
            return 0

    def remove_not_longest(self):
        self.list_of_takes_series = [s for s in self.list_of_takes_series if len(s) == self.longest_size()]

    def merge(self, other):
        self.list_of_takes_series += other.list_of_takes_series
        self._unify()
        self.remove_not_longest()

    def _unify(self):
        tup = (tuple(l) for l in self.list_of_takes_series)
        self.list_of_takes_series = list(list(x) for x in set(tup))


class Positions:
    def __init__(self, blacks, whites):
        self.blacks = blacks
        self.whites = whites

    @property
    def all(self):
        return self.blacks + self.whites

    def get_color(self, color):
        if color == Color.BLACK:
            return self.blacks
        elif color == Color.WHITE:
            return self.whites
        else:
            raise ValueError(f"Unsupported color: {color}")


def _take(start_cell, target_cell, positions):
    next_ = start_cell.get_next_in_direction(target_cell)
    if next_ in positions.all:
        return
    else:
        return Take(next_, target_cell)


def _rec_take(start_cell, target_cell, color, positions, history=None, i=0) -> Optional[PossibleTakes]:
    """This finds the longest possible takes"""
    # todo there's no need of having history? returning the list of taken in reverse order is enough. BUT!! need to keep track of taken pieces
    #  so: 2 args: taken_pieces: only taken cells in prior steps
    #              takes_series: series of Takes in reverse order, when nothing to take just return none, otherwise rec call + append current take to longest results
    tabs = '\t' * i
    header = f"{tabs}#{i} - {start_cell} / {target_cell} || "
    print(f"{header}history {history}")

    if target_cell in positions.get_color(color.opponent()):
        take = _take(start_cell, target_cell, positions)
        if take is None:
            print(f"{header}TAKE NONE")
            return PossibleTakes(history)
        else:
            if history is None:
                print(f"{header}ONGOING EMPTY")
                history = [take]
            else:
                history.append(take)

            # find neighbors of the cell we just moved to
            neighbors_next = take.moved_to.neighbors()

            # remove neighbors that have already been taken in the history
            for c in map(lambda x: x.taken, history):
                try:
                    neighbors_next.remove(c)
                except ValueError:
                    pass

            print(f"{header}Will start {len(neighbors_next)}")
            # explore neighbors
            takes_by_neighbor = [_rec_take(take.moved_to, n_, color, positions, history, i + 1) for n_ in neighbors_next]
            print(f"{header}Back with {takes_by_neighbor}")

            takes_by_neighbor = [x for x in takes_by_neighbor if x is not None]
            print(f"{header}Cleaned {takes_by_neighbor}")
            # merge the results
            merged_takes = takes_by_neighbor[0]
            for t in takes_by_neighbor[1:]:
                merged_takes.merge(t)
            print(f"{header}Merged {merged_takes}")
            print(f"{header}Longest {merged_takes.longest_size()}")
            return merged_takes
    else:
        print(f"{header}Nothing to take")
        if history is None:
            return None
        else:
            return PossibleTakes(history)


def possible_moves(current_position, color, positions):
    moves = []
    has_taken = False
    neighbors = current_position.neighbors()
    for n in neighbors:
        # check if there's a piece on the neighbor
        if n in positions.get_color(color.color):
            continue

        if not has_taken and color.move_is_forward(current_position, n):
            # if the move is forward, we can go there
            moves.append([Move(n)])
            continue

        these_moves = _rec_take(current_position, n, color, positions)
        if these_moves is not None:
            has_taken = True
            moves += these_moves.list_of_takes_series

    # only keep the the longest moves
    max_size = max(len(x) for x in moves)
    return [m for m in moves if len(m) == max_size]


if __name__ == '__main__':
    cells = [Cell(x, y) for x in range(10) for y in range(10) if (x + y) % 2 == 0]
    #black_cells = [c for c in cells if c.y >= 6]
    #white_cells = [c for c in cells if c.y <= 3]
    black_cells = [Cell(9, 3)]
    white_cells = [Cell(8, 4), Cell(6, 4), Cell(5, 5), Cell(6, 2), Cell(4, 2)]

    BLACK = Color(Color.BLACK)
    WHITE = Color(Color.WHITE)
    positions = Positions(black_cells, white_cells)

    res = possible_moves(Cell(9, 3), BLACK, positions)
    print(f"FINAL: {len(res)}")
    print(f"FINAL: {max(len(x) for x in res)}")
    print(f"FINAL: {res}")
