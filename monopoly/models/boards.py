import collections
import contextlib
import itertools
import pathlib
import pickle
import random
import typing

import pydantic

from monopoly.constants import CardType, DirectionAttr, StockType, SystemText

from .equipments import BaseCard, BasePlayer, BaseSpace
from .equipments.players import PlayerLand
from .interfaces import (
    ChainableInterface, PlayerListableInterface, PlayableMenuInterface,
    PropertyListableInterface, SavableMenuInterface,
)
from .properties import BaseLand, BaseStock


class Board(PlayerListableInterface, PropertyListableInterface, SavableMenuInterface):
    start_player: typing.Union["BoardPlayer", None] = None
    start_space: typing.Union["BoardSpace", None] = None

    lands: dict[str, BaseLand] = {}
    stocks: dict[str, BaseStock] = {}
    players: list[BasePlayer] = pydantic.Field(default_factory=list)

    cards: dict[CardType, list[BaseCard]] = collections.defaultdict(list)
    credentials: dict[str, PlayerLand] = {}

    current_player: typing.Union["BoardPlayer", None] = None
    direction: DirectionAttr = DirectionAttr.FORWARDS

    finished: bool = False

    @classmethod
    def load(cls) -> typing.Union["Board", None]:
        return cls.load_menu()

    @classmethod
    def loading(cls, filepath: pathlib.PosixPath) -> typing.Union["Board", None]:
        try:
            return pickle.loads(filepath.read_bytes())
        except (EOFError, pickle.UnpicklingError):
            print(SystemText.LOADING_FAILED.value)
        return None

    @property
    def dice(self) -> int:
        return random.randint(1, 6)

    @property
    def playable_players(self) -> typing.Generator["BoardPlayer", None, None]:
        yield from filter(lambda player: player.playable, self.board_players)

    @property
    def board_players(self) -> typing.Generator["BoardPlayer", None, None]:
        player = self.start_player
        while True:
            yield player
            player = getattr(player, self.direction.value)()
            if player == self.start_player:
                return

    @property
    def poorest_player(self) -> BasePlayer:
        return self.get_the_most_player(
            lambda x, y: x.player.cash > y.player.cash,
        ).player

    @property
    def richest_player(self) -> BasePlayer:
        return self.get_the_most_player(
            lambda x, y: x.player.cash < y.player.cash,
        ).player

    @property
    def winner(self) -> "BoardPlayer":
        winners = tuple(self.playable_players)
        assert len(winners) == 1
        return winners[0]

    def buy_stock(self, player: BasePlayer):
        with contextlib.suppress(self.Cancelled):
            while True:
                print(f"{player} 想買入哪檔股票呢？")
                self.list_stocks()

                try:
                    self.stocks[self.cancelable_command].buy(player, self)
                except KeyError:
                    print(SystemText.PROPERTY_CODE_ERROR.value)

    def delete_or_skip_credential(self, land: BaseLand):
        with contextlib.suppress(KeyError):
            self.credentials.pop(land.id)

    def get_or_create_credential(
        self,
        land: BaseLand,
        credential: typing.Union[PlayerLand, None] = None,
    ):
        with contextlib.suppress(KeyError):
            return self.credentials[land.id]

        assert credential is not None
        self.credentials[land.id] = credential
        return credential

    def get_the_most_player(
        self,
        func: typing.Callable[["BoardPlayer", "BoardPlayer"], bool],
        playable: bool = True,
    ) -> "BoardPlayer":
        players = self.board_players
        if playable:
            players = self.playable_players

        result = self.current_player
        for player in players:
            if func(result, player):
                result = player
        return result

    def list_land_detail(self, land: BaseLand) -> tuple:
        credential = self.credentials.get(land.id)

        player = getattr(credential, "player", SystemText.UNDEFINED.value)
        houses = getattr(credential, "houses", SystemText.UNDEFINED.value)
        if not land.buildable:
            houses = SystemText.UNDEFINED.value

        net_worth = getattr(credential, "net_worth", SystemText.UNDEFINED.value)
        if isinstance(net_worth, int):
            net_worth = f"{net_worth:,}"

        return (
            land.id,
            land.name,
            f"{land.land_price:,}",
            str(player),
            houses,
            net_worth,
        )

    def list_player_detail(self, player: BasePlayer) -> tuple:
        return (
            player.name,
            player.cash,
            player.land_worth + player.house_worth,
            player.stock_worth,
            player.net_worth,
            str(player.bankruptcy),
            str(player.surrender),
        )

    def list_stock_detail(self, stock: BaseStock) -> tuple:
        return (
            stock.id,
            stock.name,
            f"{stock.value:,}",
            stock.amount,
            SystemText.UNDEFINED.value,
            SystemText.UNDEFINED.value,
        )

    def opening_stocks(self):
        print(SystemText.OPENING_STOCKS.value)
        for stock in itertools.chain(
            filter(lambda stock: stock.type == StockType.STOCK, self.stocks.values()),
            filter(lambda stock: stock.type == StockType.ETF, self.stocks.values()),
        ):
            stock.opening(board=self)

    def pause(self, player: BasePlayer, value: int):
        assert self.current_player.player == player
        self.current_player.unmovable += value

    def reverse_direction(self):
        if self.direction == DirectionAttr.FORWARDS:
            self.direction = DirectionAttr.BACKWARDS
        else:
            self.direction = DirectionAttr.FORWARDS

    def run(self):
        self.show()
        if self.current_player.playable:
            self.current_player.play()

        self.current_player = getattr(self.current_player, self.direction.value)()
        if self.current_player == self.start_player:
            self.opening_stocks()

        with contextlib.suppress(AssertionError):
            print(f"{self.winner} 優勝!!")
            self.finished = True

    def save(self):
        self.save_menu()

    def saving(self, filepath: pathlib.PosixPath):
        filepath.write_bytes(pickle.dumps(self))

    def set_free_tolling(self, player: BasePlayer):
        assert self.current_player.player == player
        self.current_player.can_free_tolling = True

    def set_three_dices(self, player: BasePlayer):
        assert self.current_player.player == player
        self.current_player.can_three_dices = True

    def show(self):
        from monopoly.viewers import BoardViewer
        BoardViewer(self).view()

    def start(self):
        self.current_player = self.start_player
        for player in self.board_players:
            self.players.append(player.player)
            player.space = self.start_space

    def take_free_tolling(self, player: BasePlayer) -> bool:
        assert self.current_player.player == player
        result = self.current_player.can_free_tolling
        self.current_player.can_free_tolling = False
        return result

    def take_three_dices(self, player: BasePlayer) -> bool:
        assert self.current_player.player == player
        result = self.current_player.can_three_dices
        self.current_player.can_three_dices = False
        return result

    def transport_start_point(
        self,
        player: BasePlayer,
        *,
        as_arrive: bool = False,
    ):
        assert self.current_player.player == player
        self.current_player.space = self.start_space
        self.current_player.pass_by()
        if as_arrive:
            self.current_player.arrive()


class BoardPlayer(ChainableInterface, PlayableMenuInterface):
    board: Board
    player: BasePlayer
    unmovable: int = 0
    space: typing.Union["BoardSpace", None] = None

    can_free_tolling: bool = False
    can_three_dices: bool = False

    backwards: typing.Union["BoardPlayer", None] = None
    forwards: typing.Union["BoardPlayer", None] = None

    @property
    def playable(self) -> bool:
        return not (self.player.bankruptcy or self.player.surrender)

    def arrive(self):
        self.space.space.arrive(self.player, board=self.board)

    def get_backwards(self) -> typing.Union["BoardPlayer", None]:
        return self.backwards

    def get_forwards(self) -> typing.Union["BoardPlayer", None]:
        return self.forwards

    def moving(self, point: int):
        while point > 0:
            next_space = getattr(self.space, self.board.direction.value)()
            if isinstance(next_space, list):
                print(f"{self.player} 選擇要往哪裡走～")
                for idx, space in enumerate(next_space):
                    print(f"[{idx}] {space.space}")

                index = 0
                with contextlib.suppress(ValueError):
                    index = max(min(int(input("> ")), len(next_space) - 1), 0)

                next_space = next_space[index]

            point -= next_space.space.moving_point
            if point >= 0:
                self.space = next_space
                self.pass_by()

        self.arrive()

    def pass_by(self):
        self.space.space.pass_by(self.player, board=self.board)

    def play(self):
        if self.unmovable > 0:
            print(f"{self.player} 暫停一次!")
            self.unmovable -= 1
            input(SystemText.PRESS_ENTER_TO_CONTINUE.value)
            return

        with contextlib.suppress(self.Cancelled):
            while self.playable:
                self.play_menu(self.player, self.board)

    def playing(self):
        minimum = 1
        maximum = 3 if self.board.take_three_dices(self.player) else 2
        print(f"{self.player} 要使用幾顆骰子？(1-{maximum})")

        number = maximum
        with contextlib.suppress(ValueError):
            number = max(min(int(input("> ")), maximum), minimum)

        dices = [self.board.dice for _ in range(number)]
        print("{} 骰到 {} 共 {} 點".format(
            str(self.player),
            ", ".join(map(str, dices)),
            str(sum(dices)),
        ))

        self.moving(sum(dices))
        raise self.Cancelled

    def set_backwards(self, other: "BoardPlayer"):
        self.backwards = other

    def set_forwards(self, other: "BoardPlayer"):
        self.forwards = other

    def __eq__(self, other: "BoardPlayer") -> bool:
        return self.player == other.player

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.player)


class BoardSpace(ChainableInterface):
    board: Board
    space: BaseSpace

    backwards: list["BoardSpace"] = pydantic.Field(default_factory=list)
    forwards: list["BoardSpace"] = pydantic.Field(default_factory=list)

    def get_backwards(self) -> typing.Union[list["BoardSpace"], "BoardSpace", None]:
        if len(self.backwards) > 1:
            return self.backwards
        if self.backwards:
            return self.backwards[0]
        return None

    def get_forwards(self) -> typing.Union[list["BoardSpace"], "BoardSpace", None]:
        if len(self.forwards) > 1:
            return self.forwards
        if self.forwards:
            return self.forwards[0]
        return None

    def set_backwards(self, other: "BoardSpace"):
        self.backwards.append(other)

    def set_forwards(self, other: "BoardSpace"):
        self.forwards.append(other)

    def __eq__(self, other: "BoardSpace") -> bool:
        return self.space == other.space

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return str(self.space)
