import abc

from monopoly.models.boards import Board


class BaseLoader(abc.ABC):
    def execute(self, **kwargs) -> Board:
        board = Board()
        self._prepare_loading(**kwargs)

        # load properties
        self.load_lands(board, **kwargs)
        self.load_stocks(board, **kwargs)
        self.load_etfs(board, **kwargs)

        # load equipments
        self.load_cards(board, **kwargs)
        self.load_spaces(board, **kwargs)
        self.load_players(board, **kwargs)
        return board

    @abc.abstractmethod
    def load_cards(self, board: Board, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def load_etfs(self, board: Board, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def load_lands(self, board: Board, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def load_players(self, board: Board, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def load_stocks(self, board: Board, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def load_spaces(self, board: Board, **kwargs):
        raise NotImplementedError

    def _prepare_loading(self, **kwargs):
        pass
