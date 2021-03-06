from __future__ import annotations

from collections import deque
from typing import List, Optional, Set, Tuple, Union


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
        return self.position == other.position

    def __hash__(self):
        return hash(self.position)

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

    def __repr__(self):
        return f"Move({self.moved_to})"

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.moved_to == other.moved_to

    def __hash__(self):
        return hash(self.moved_to)


class Take(Move):
    def __init__(self, moved_to: Cell, taken: Cell):
        super().__init__(moved_to)
        self.taken = taken
        self.moved_to = moved_to

    def __repr__(self):
        return f"Take({self.moved_to} by {self.taken})"

    def __eq__(self, other):
        if not isinstance(other, Take):
            return False
        return self.moved_to == other.moved_to and self.taken == other.taken

    def __hash__(self):
        return hash((str(self.moved_to), str(self.taken)))


class PossibleTakes:
    def __init__(self, takes: deque[Take] = None):
        self.list_of_takes_series: List[deque[Take]] = []
        if takes is not None:
            self.list_of_takes_series.append(takes)

    def __len__(self):
        return len(self.list_of_takes_series)

    def __repr__(self):
        return f"PossibleTakes({self.list_of_takes_series})"

    @staticmethod
    def from_all(*args) -> PossibleTakes:
        res = PossibleTakes()
        for other in args:
            if other is None:
                continue
            res.merge(other)
        return res

    def prepend(self, take: Take):
        for x in self.list_of_takes_series:
            x.insert(0, take)

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

    def settify(self):
        return set(tuple(l) for l in self.list_of_takes_series)

    def _unify(self):
        tup = (tuple(l) for l in self.list_of_takes_series)
        self.list_of_takes_series = [deque(x) for x in set(tup)]


class Positions:
    def __init__(self, blacks=None, whites=None):
        if blacks is None and whites is None:
            cells = [Cell(x, y) for x in range(10) for y in range(10) if (x + y) % 2 == 0]
            blacks = [c for c in cells if c.y >= 6]
            whites = [c for c in cells if c.y <= 3]
        elif blacks is None:
            blacks = []
        elif whites is None:
            whites = []
        self.blacks = blacks
        self.whites = whites

    @property
    def all(self):
        return self.blacks + self.whites

    def get(self, color):
        if color == Color.BLACK:
            return self.blacks
        elif color == Color.WHITE:
            return self.whites
        else:
            raise ValueError(f"Unsupported color: {color}")

    def color_of(self, cell: Cell) -> Optional[Color]:
        if cell in self.blacks:
            return BLACK
        elif cell in self.whites:
            return WHITE
        else:
            return None


def _take(start_cell, target_cell, positions):
    next_ = start_cell.get_next_in_direction(target_cell)
    if next_ in positions.all:
        return
    else:
        return Take(next_, target_cell)


def _rec_take(start_cell, target_cell, color, positions, takes_series=None, i=0) -> Optional[PossibleTakes]:
    """This finds the longest possible takes, returned IN REVERSE ORDER"""
    tabs = '\t' * i
    header = f"{tabs}#{i} - {start_cell} / {target_cell} || "
    print(f"{header}takes series {takes_series}")

    if target_cell in positions.get(color.opponent()):
        take = _take(start_cell, target_cell, positions)
        if take is None:
            print(f"{header}TAKE NONE")
            return None
        else:
            if takes_series is None:
                print(f"{header}TAKES SERIES EMPTY")
                takes_series = [target_cell]
            else:
                takes_series.append(target_cell)

            # find neighbors of the cell we just moved to
            neighbors_next = take.moved_to.neighbors()

            # remove neighbors that have already been taken in the history
            for c in takes_series:
                try:
                    neighbors_next.remove(c)
                except ValueError:
                    pass

            print(f"{header}Will explore {len(neighbors_next)} neighbors")
            # explore neighbors
            takes_by_neighbor = [_rec_take(take.moved_to, n_, color, positions, takes_series, i + 1) for n_ in neighbors_next]
            print(f"{header}Back with {takes_by_neighbor}")

            # merge the results
            merged_takes = PossibleTakes.from_all(*takes_by_neighbor)
            print(f"{header}Merged {merged_takes}")
            print(f"{header}Longest {merged_takes.longest_size()}")
            print(f"{header}Will add {take}")
            if merged_takes.longest_size() == 0:
                merged_takes = PossibleTakes(deque([take]))
            else:
                merged_takes.prepend(take)
            print(f"{header}Added {merged_takes}")
            return merged_takes
    else:
        print(f"{header}NOT OPPONENT")
        return None


def legal_moves(current_position: Cell, positions: Positions) -> Union[Set[Move], Set[Tuple[Take]]]:
    """
    Find every legal moves, starting from this current position and given these positions

    :param current_position:
    :param positions:
    :return: a set of Moves if no takes are possible or a set of tuples of Takes if takes are possible
    """
    color = positions.color_of(current_position)
    moves = set()
    has_taken = False
    neighbors = current_position.neighbors()
    for n in neighbors:
        # check if there's a piece of the current color on the neighbor
        if n in positions.get(color.color):
            continue

        # if the cell is forward and moves contains no Takes yet
        if not has_taken and color.move_is_forward(current_position, n):
            # if the move is forward, we can go there
            moves.add(Move(n))
            continue

        # otherwise try to take the piece
        these_moves = _rec_take(current_position, n, color, positions)
        if these_moves is not None:
            if not has_taken:
                has_taken = True
                # reinitialize moves
                moves = set()
            moves.update(these_moves.settify())

    return moves


BLACK = Color(Color.BLACK)
WHITE = Color(Color.WHITE)


if __name__ == '__main__':
    black_cells = [Cell(9, 3)]
    white_cells = [Cell(8, 4), Cell(6, 4), Cell(5, 5), Cell(6, 2), Cell(4, 2)]

    positions = Positions(black_cells, white_cells)

    res = legal_moves(Cell(9, 3), positions)
    print(f"FINAL: {len(res)}")
    print(f"FINAL: {res}")
