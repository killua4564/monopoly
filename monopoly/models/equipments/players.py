import abc
import contextlib
import itertools

import pydantic

from monopoly import configs
from monopoly.constants import Area, SystemText

from ..interfaces import (
    BuildableMenuInterface, PropertyListableInterface,
    PropertyTradingOffMenuInterface, ShowableModelInterface,
)
from ..properties import BaseLand, BaseStock


class BasePlayer(ShowableModelInterface, PropertyListableInterface, abc.ABC):
    name: str = pydantic.Field(..., min_length=1, max_length=6)
    cash: int = configs.PLAYER_DEFAULT_CASH
    incoming: int = 0

    bankruptcy: bool = False
    surrender: bool = False

    lands: dict[str, "PlayerLand"] = {}
    stocks: dict[str, "PlayerStock"] = {}

    @property
    def house_worth(self) -> int:
        return sum(land.house_worth for land in self.lands.values())

    @property
    def land_worth(self) -> int:
        return sum(land.land_worth for land in self.lands.values())

    @property
    def net_worth(self) -> int:
        return self.cash + sum(
            player_property.net_worth
            for player_property in itertools.chain(
                self.lands.values(),
                self.stocks.values(),
            )
        )

    @property
    def stock_worth(self) -> int:
        return sum(stock.stock_worth for stock in self.stocks.values())

    def bankrupt(self, board: "Board"):
        for land in tuple(self.lands.values()):
            while land.houses:
                land.demolition(board, silent=True)
            land.land.selling(self, board, silent=True)

        for stock in tuple(self.stocks.values()):
            while stock.amount:
                stock.stock.selling(self, board, silent=True)

        self.bankruptcy = True
        print(f"{self} 宣告破產!!")

    def count_area_lands(self, area: Area) -> int:
        return len(tuple(filter(
            lambda land: land.land.area == area,
            self.lands.values(),
        )))

    def delete_or_skip_player_land(self, land: BaseLand):
        with contextlib.suppress(KeyError):
            self.lands.pop(land.id)

    def delete_or_skip_player_stock(self, stock: BaseStock):
        with contextlib.suppress(KeyError):
            self.stocks.pop(stock.id)

    def earn(self, value: int, income_tax_free: bool = False):
        self.cash += value
        if not income_tax_free:
            self.incoming += value

    def get_or_create_player_land(
        self,
        land: BaseLand,
        *,
        houses: int = 0,
    ) -> "PlayerLand":
        with contextlib.suppress(KeyError):
            return self.lands[land.id]

        self.lands[land.id] = PlayerLand(
            player=self, land=land, houses=houses,
        )
        return self.lands[land.id]

    def get_or_create_player_stock(
        self,
        stock: BaseStock,
        *,
        amount: int = 0,
    ) -> "PlayerStock":
        with contextlib.suppress(KeyError):
            return self.stocks[stock.id]

        self.stocks[stock.id] = PlayerStock(
            player=self, stock=stock, amount=amount,
        )
        return self.stocks[stock.id]

    def list_land_detail(self, land: "PlayerLand") -> tuple:
        houses = land.houses
        if not land.land.buildable:
            houses = SystemText.UNDEFINED.value

        return (
            land.land.id,
            land.land.name,
            f"{land.land.land_price:,}",
            land.player.name,
            houses,
            f"{land.net_worth:,}",
        )

    def list_stock_detail(self, stock: "PlayerStock") -> tuple:
        return (
            stock.stock.id,
            stock.stock.name,
            f"{stock.stock.value:,}",
            stock.amount,
            f"{stock.net_worth:,}",
        )

    def pay(self, value: int):
        self.cash -= value

    def prepare_payment(
        self,
        board: "Board",
        value: int,
        *,
        force: bool = False,
    ):
        if self.net_worth < value:
            if force:
                print(f"{self} 淨資產不足!!")
                self.bankrupt(board)
                input(SystemText.PRESS_ENTER_TO_CONTINUE.value)
            return force

        while self.cash < value:
            print(f"{self} 存款不足，請變賣資產!!")
            self.trade_off(board)
            if not force:
                break

        return self.cash >= value

    def show(self):
        self.show_divider()
        self.show_player_info()
        self.show_horizontal()
        self.show_worth_info()
        self.show_divider()
        self.list_lands()
        self.list_stocks()

    def show_player_info(self):
        self.print_row(
            f"{'名稱：':>{self._width // 2 - 3}}"
            f"{self.name:<{self._width // 2}}"
        )
        self.print_row(
            f"{'存款：':>{self._width // 2 - 3}}"
            f"{f'${self.cash:,}':<{self._width // 2}}"
        )
        self.print_row(
            f"{'淨值：':>{self._width // 2 - 3}}"
            f"{f'${self.net_worth:,}':<{self._width // 2}}"
        )

    def show_worth_info(self):
        self.print_row(
            f"{'土地價值：':>{self._width // 2 - 5}}"
            f"{f'${self.land_worth:,}':<{self._width // 2}}"
        )
        self.print_row(
            f"{'房屋價值：':>{self._width // 2 - 5}}"
            f"{f'${self.house_worth:,}':<{self._width // 2}}"
        )
        self.print_row(
            f"{'股票價值：':>{self._width // 2 - 5}}"
            f"{f'${self.stock_worth:,}':<{self._width // 2}}"
        )

    @abc.abstractmethod
    def trade_off(self, *args, **kwargs):
        raise NotImplementedError

    def __eq__(self, other: "BasePlayer") -> bool:
        return self.name == other.name

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.name


class Player(BasePlayer, PropertyTradingOffMenuInterface):
    def trade_off(self, board: "Board"):
        with contextlib.suppress(self.Cancelled):
            while True:
                self.trade_off_menu(board)

    def trading_lands_off(self, board: "Board"):
        with contextlib.suppress(self.Cancelled):
            while True:
                print(f"{self} 想要變賣哪個不動產呢？")
                self.list_lands()

                try:
                    land = self.lands[self.cancelable_command]
                    if land.land.buildable and land.houses > 0:
                        land.demolish(board)
                    else:
                        land.land.sell(self, board)
                except KeyError:
                    print(SystemText.PROPERTY_CODE_ERROR.value)

    def trading_stocks_off(self, board: "Board"):
        with contextlib.suppress(self.Cancelled):
            while True:
                print(f"{self} 想要變賣哪張股票呢？")
                self.list_stocks()

                try:
                    self.stocks[self.cancelable_command].stock.sell(self, board)
                except KeyError:
                    print(SystemText.PROPERTY_CODE_ERROR.value)


class PlayerLand(BuildableMenuInterface):
    player: BasePlayer
    land: BaseLand
    houses: int = pydantic.Field(0, ge=0, le=configs.BUILDING_UPPERBOUND)

    @property
    def house_worth(self) -> int:
        if not self.land.buildable:
            return 0
        return self.land.house_price * self.houses

    @property
    def land_worth(self) -> int:
        return self.land.land_price

    @property
    def net_worth(self) -> int:
        return self.land.sale_value + self.sale_value * self.houses

    @property
    def sale_value(self) -> int:
        if not self.land.buildable:
            return 0
        return int(self.land.house_price * configs.HOUSE_DISCOUNT_RATE)

    @property
    def tolling_value(self) -> int:
        base_value = self.land.tolls[self.houses]
        area_count = self.player.count_area_lands(self.land.area)
        addition_rate = (area_count - 1) * configs.AREA_ADDITION_RATE
        return base_value * (1 + addition_rate)

    @property
    def worth(self) -> int:
        return self.house_worth + self.land_worth

    def construct(self, board: "Board"):
        assert self.land.buildable
        with contextlib.suppress(self.Cancelled):
            while self.houses < configs.BUILDING_UPPERBOUND:
                self.construct_menu(self.player, board)

    def construction(self, board: "Board", is_free: bool = False):
        assert self.land.buildable and self.houses < configs.BUILDING_UPPERBOUND
        if not is_free:
            if not self.player.prepare_payment(board, self.land.house_price):
                return

            try:
                assert board.get_or_create_credential(self.land).player == self.player
                self.player.pay(self.land.house_price)
            except AssertionError as error:
                raise self.Cancelled() from error

        self.land.stock.earn(self.land.house_price)
        self.houses += 1
        print(SystemText.CONSTRUCTION_SUCCESS.value)
        if not configs.UNLIMITED_BUILDING:
            raise self.Cancelled()

    def demolish(self, board: "Board"):
        assert self.land.buildable
        with contextlib.suppress(self.Cancelled):
            while self.houses > 0:
                self.demolish_menu(self.player, board)

    def demolition(self, *args, silent: bool = False):
        assert self.land.buildable and self.houses > 0
        self.player.earn(self.sale_value, income_tax_free=True)
        self.land.stock.pay(self.sale_value)
        self.houses -= 1
        if not silent:
            print(SystemText.DEMOLITION_SUCCESS.value)

    def show(self):
        self.land.show(houses=self.houses)

    def tolling(self, player: BasePlayer, board: "Board"):
        if board.take_free_tolling(player):
            print(f"{player} 可免付過路費")
            input(SystemText.PRESS_ENTER_TO_CONTINUE.value)
            return

        value: int = self.tolling_value
        print(f"{player} 需要支付 {self.land} 的過路費 ${value} 給 {self.player}")
        input(SystemText.PRESS_ENTER_TO_CONTINUE.value)

        player.prepare_payment(board, value, force=True)
        player.pay(value)
        self.player.earn(value)
        self.land.stock.earn(value)

    def __str__(self) -> str:
        return str(self.land)


class PlayerStock(pydantic.BaseModel):
    player: BasePlayer
    stock: BaseStock
    amount: int = 0

    @property
    def net_worth(self) -> int:
        return self.stock.sale_value * self.amount

    @property
    def stock_worth(self) -> int:
        return self.stock.value * self.amount

    def decrease(self):
        assert self.amount > 0
        self.amount -= 1
        if self.amount == 0:
            self.player.delete_or_skip_player_stock(self.stock)

    def increase(self):
        self.amount += 1

    def __str__(self) -> str:
        return str(self.stock)
