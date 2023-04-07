import abc
import contextlib
import sys
import typing

from . import configs
from .constants import SystemText
from .loaders import FixtureLoader
from .models import Board
from .models.interfaces import EnginelizeMenuInterface


class BaseEngine(EnginelizeMenuInterface, abc.ABC):
    title: str = SystemText.GAME_TITLE.value

    board: typing.Union[Board, None] = None

    @abc.abstractmethod
    def execute(self, *args, **kwargs):
        raise NotImplementedError

    def execution_load(self):
        try:
            self.board = Board.load()
        except Exception as error:
            self.handle_exception(error)

    def execution_new(self, *args, **kwargs):
        try:
            self.board = FixtureLoader().execute()
            self.board.start()
        except Exception as error:
            self.handle_exception(error)

    def execution_staff(self, *args, **kwargs):
        print(SystemText.GAME_STAFF.value)

    def handle_exception(self, error: Exception):
        if self.board is not None:
            self.board.auto_saving()
        print(SystemText.UNEXPECTED_ERROR.value)
        if configs.DEBUG_MODE:
            raise error
        sys.exit(1)


class StandAloneEngine(BaseEngine):
    def execute(self):
        try:
            with contextlib.suppress(
                EOFError,
                KeyboardInterrupt,
                self.Cancelled,
            ):
                while self.board is None:
                    self.execute_menu(self.title)
                while self.board.finished is False:
                    self.board.run()
            print(SystemText.GAME_OVER.value)
        except Exception as error:
            self.handle_exception(error)
