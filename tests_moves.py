from collections import deque

from main import possible_moves, Cell, Color, Take, PossibleTakes, Positions


class TestPossibleMoves:
    def _test_takes_base(self, result, *args):
        expected = PossibleTakes.from_all(*[PossibleTakes(deque(l)) for l in args]).list_of_takes_series
        assert result == expected

    def test_1(self):
        positions = Positions([Cell(9, 3)], [Cell(8, 4), Cell(6, 4), Cell(6, 2), Cell(5, 5), Cell(4, 2)])
        result = possible_moves(Cell(9, 3), positions)
        r1 = [Take(Cell(7, 5), Cell(8, 4)), Take(Cell(5, 3), Cell(6, 4)), Take(Cell(7, 1), Cell(6, 2))]
        r2 = [Take(Cell(7, 5), Cell(8, 4)), Take(Cell(5, 3), Cell(6, 4)), Take(Cell(3, 1), Cell(4, 2))]
        self._test_takes_base(result, r1, r2)