import contextlib
import typing

import pydantic

from monopoly.models import Board


class BoardViewer:
    class Space(pydantic.BaseModel):
        name: str
        houses: int = 0
        usernames: list[str] = pydantic.Field(default_factory=list)

    deltas: list[tuple[int, int]] = [
        (0, -1), (-1, 0), (0, 1), (1, 0),
    ]

    def __init__(
        self,
        board: Board,
        board_size: int = 11,
        space_width: int = 16,
    ):
        self.board = board
        self.board_size = board_size
        self.space_width = space_width
        self.views = [[None] * board_size for _ in range(board_size)]
        self._prepare()

    def _prepare(self):
        players = tuple(self.board.board_players)
        current_space = self.board.start_space
        diagonal_space = None

        def _prepare_space(x: int, y: int):
            self.views[x][y] = self.Space(name=current_space.space.name)
            with contextlib.suppress(AttributeError, KeyError):
                self.views[x][y].houses = self.board.credentials[
                    current_space.space.land.id
                ].houses

            self.views[x][y].usernames = [
                player.player.name
                for player in players
                if player.space == current_space
            ]

        # handle surrounding
        x, y = self.board_size - 1, self.board_size - 1
        for dx, dy in self.deltas:
            while all((
                0 <= x + dx < self.board_size,
                0 <= y + dy < self.board_size,
            )):
                _prepare_space(x, y)
                x, y = x + dx, y + dy
                current_space = current_space.get_forwards()
                if isinstance(current_space, list):
                    current_space, diagonal_space = current_space

        # handle diagonal
        x, y, dx, dy = self.board_size - 2, 1, -1, 1
        current_space = diagonal_space
        for _ in range(1, self.board_size - 2):
            _prepare_space(x, y)
            x, y = x + dx, y + dy
            current_space = current_space.get_forwards()

    def view(self):
        def _view_column(column: typing.Union[self.Space, None]) -> typing.Generator[str, None, None]:
            if column is None:
                yield from (" " * self.space_width for _ in range(5))
                return

            yield "-" * self.space_width
            yield f"{'🏠' * column.houses:^{self.space_width - column.houses}}"
            yield f"{column.name:^{self.space_width - self.board.chinese_length(column.name)}}"
            yield f"{','.join(column.usernames):^{self.space_width - self.board.chinese_length(column.usernames)}}"
            yield "-" * self.space_width

        for row in self.views:
            column_viewers: list[typing.Generator[str, None, None]] = [
                _view_column(column) for column in row
            ]

            for _ in range(5):
                print("|{}|".format("|".join(next(column) for column in column_viewers)))
