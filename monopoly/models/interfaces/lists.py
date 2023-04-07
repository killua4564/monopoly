import abc
import typing

from monopoly.constants import SystemText

from .models import BaseViewableModelInterface, CancelableModelInterface


class BaseListableInterface(BaseViewableModelInterface, CancelableModelInterface, abc.ABC):
    _column_width: int = 14

    @property
    def cancelable_command(self) -> str:
        print(SystemText.LISTABLE_CANCEL.value)
        command = input("> ").upper()
        if command == "C":
            raise self.Cancelled()
        return command

    def list_columns(self, columns: typing.Iterable):
        print("|{}|".format("|".join(
            f"{column:^{self._column_width - self.chinese_length(column)}}"
            for column in columns
        )))

    def list_divider(self, headers: tuple):
        print("+{}+".format("+".join("-" * self._column_width for _ in headers)))


class PlayerListableInterface(BaseListableInterface, abc.ABC):
    players: typing.Iterable[typing.Any] = []

    @abc.abstractmethod
    def list_player_detail(self, player: typing.Any) -> tuple:
        raise NotImplementedError

    @property
    def list_player_header(self) -> tuple:
        return ("名稱", "存款", "不動產", "股票", "淨值", "破產", "投降")

    def list_players(self):
        self.list_divider(self.list_player_header)
        self.list_columns(self.list_player_header)
        self.list_divider(self.list_player_header)
        for player in self.players:
            self.list_columns(self.list_player_detail(player))
        self.list_divider(self.list_player_header)


class PropertyListableInterface(BaseListableInterface, abc.ABC):
    lands: dict[str, typing.Any] = {}
    stocks: dict[str, typing.Any] = {}

    @abc.abstractmethod
    def list_land_detail(self, land: typing.Any) -> tuple:
        raise NotImplementedError

    @property
    def list_land_header(self) -> tuple:
        return ("代碼", "名稱", "價格", "擁有者", "建數", "淨值")

    def list_lands(self):
        self.list_divider(self.list_land_header)
        self.list_columns(self.list_land_header)
        self.list_divider(self.list_land_header)
        for land in self.lands.values():
            self.list_columns(self.list_land_detail(land))
        self.list_divider(self.list_land_header)

    @abc.abstractmethod
    def list_stock_detail(self, stock: typing.Any) -> tuple:
        raise NotImplementedError

    @property
    def list_stock_header(self) -> tuple:
        return ("代碼", "名稱", "價格", "張數", "淨值", "損益")

    def list_stocks(self):
        self.list_divider(self.list_stock_header)
        self.list_columns(self.list_stock_header)
        self.list_divider(self.list_stock_header)
        for stock in self.stocks.values():
            self.list_columns(self.list_stock_detail(stock))
        self.list_divider(self.list_stock_header)
