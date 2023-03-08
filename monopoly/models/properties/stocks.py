import abc
import contextlib
import math
import random
import typing

import pydantic

from monopoly import configs
from monopoly.constants import StockType, SystemText, TaxFee

from ..interfaces import TradableMenuInterface


class BaseStock(TradableMenuInterface, abc.ABC):
    id: str
    name: str
    type: StockType

    value: int
    amount: int = pydantic.Field(..., ge=0)
    spread: int = 0
    histories: list[int] = []
    transfer_tax: float

    @property
    def sale_value(self) -> int:
        return math.ceil(self.value * (1 - self.transfer_tax))

    def buy(self, player: "BasePlayer", board: "Board"):
        with contextlib.suppress(self.Cancelled):
            while self.amount > 0:
                self.buy_menu(player, board)

    def buying(self, player: "BasePlayer", board: "Board"):
        assert self.amount > 0
        if not player.prepare_payment(board, self.value):
            return

        player.pay(self.value)
        player.get_or_create_player_stock(self).increase()
        self.amount -= 1
        print(SystemText.BUYING_SUCCESS.value)

    def sell(self, player: "BasePlayer", board: "Board"):
        with contextlib.suppress(self.Cancelled):
            player_stock = player.get_or_create_player_stock(self)
            while player_stock.amount > 0:
                self.sell_menu(player, board)

    def selling(
        self,
        player: "BasePlayer",
        board: "Board",
        *,
        silent: bool = False,
    ):
        player.get_or_create_player_stock(self).decrease()
        player.earn(self.sale_value, income_tax_free=True)
        self.amount += 1
        if not silent:
            print(SystemText.SELLING_SUCCESS.value)

    @abc.abstractmethod
    def opening(self, *args, **kwargs):
        raise NotImplementedError

    def set_history(self):
        self.histories = [self.spread] + self.histories[:10]

    def show(self):
        self.show_divider()
        self.show_base_info()
        self.show_horizontal()
        self.show_stock_info()
        self.show_horizontal()
        self.show_history_info()
        self.show_horizontal()
        self.show_stock_detail()
        self.show_divider()

    def show_base_info(self):
        self.print_row(
            f"{self.id:^{self._width // 2}}"
            f"{self.name:^{self._width // 2 - self.chinese_length(self.name)}}"
        )

    def show_history_info(self):
        self.print_row(
            f"{'近十次歷史：':>{self._width // 2 - 6}}"
            f"{' ' * (self._width // 2)}"
        )
        for idx, history in enumerate(self.histories, 1):
            self.print_row(
                f"{f'前{idx:02}次：':>{self._width // 2 - 3}}"
                f"{f'{history:+}':<{self._width // 2}}"
            )

    @abc.abstractmethod
    def show_stock_detail(self):
        raise NotImplementedError

    def show_stock_info(self):
        self.print_row(
            f"{'價格：':>{self._width // 2 - 3}}"
            f"{f'{self.value:02}':<{self._width // 2}}"
        )
        self.print_row(
            f"{'漲跌：':>{self._width // 2 - 3}}"
            f"{f'{self.spread:+}':<{self._width // 2}}"
        )
        self.print_row(
            f"{'剩餘：':>{self._width // 2 - 3}}"
            f"{f'{self.amount:02}':<{self._width // 2}}"
        )

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.id} {self.name}"


class Stock(BaseStock):
    type: StockType = StockType.STOCK
    land: typing.Union["Land", None] = None

    beta: float
    esg_ratio: float = pydantic.Field(..., ge=.0, le=1.)
    payout_ratio: float = pydantic.Field(..., ge=.0, le=1.)

    earning: int = 0
    payment: int = 0
    transfer_tax: float = TaxFee.STOCK_TRANSFER_TAX.value

    def lands_affect(self, board: "Board") -> int:
        if not getattr(self.land, "has_owner", False):
            return 0

        credential = board.get_or_create_credential(self.land)
        base = configs.STOCK_SHUFFLE_BASE * self.beta * self.esg_ratio
        return int(base * credential.houses / configs.BUILDING_UPPERBOUND)

    def earn(self, value: int):
        self.earning += int(value * self.payout_ratio)

    def opening(self, *, board: "Board"):
        base = int(configs.STOCK_SHUFFLE_BASE * self.beta)
        shuffle = random.randint(-base, base)
        self.spread = shuffle + self.earning - self.payment + self.lands_affect(board)
        self.value = self.value + self.spread
        self.earning = self.payment = 0
        self.set_history()

    def pay(self, value: int):
        self.payment += int(value * self.payout_ratio)

    def show_stock_detail(self):
        self.print_row(
            f"{'風險值：':>{self._width // 2 - 4}}"
            f"{round(self.beta, 2):<{self._width // 2}}"
        )
        self.print_row(
            f"{'ESG 分數：':>{self._width // 2 - 3}}"
            f"{int(100 * self.esg_ratio):<{self._width // 2}}"
        )
        self.print_row(
            f"{'盈餘分配率：':>{self._width // 2 - 6}}"
            f"{f'{int(100 * self.payout_ratio)}%':<{self._width // 2}}"
        )


class ETF(BaseStock):
    class Constituent(pydantic.BaseModel):
        stock: Stock
        percent: float

        @property
        def spread(self) -> float:
            return self.stock.spread * self.percent

        @property
        def value(self) -> float:
            return self.stock.value * self.percent

    type: StockType = StockType.ETF
    value: int = 1000

    expense_ratio: float
    constituents: list[Constituent] = []
    transfer_tax: float = TaxFee.ETF_TRANSFER_TAX.value

    def opening(self, **kwargs):
        spread = sum(constituent.spread for constituent in self.constituents)
        self.spread = int(spread)
        self.value = math.ceil((self.value + spread) * (1 - self.expense_ratio))
        self.set_history()

    def reset(self):
        self.value = int(sum(constituent.value for constituent in self.constituents))

    def show_stock_detail(self):
        self.print_row(
            f"{'管理費用率：':>{self._width // 2 - 6}}"
            f"{f'{round(100 * self.expense_ratio, 2)}%':<{self._width // 2}}"
        )
        self.show_horizontal()
        self.print_row(
            f"{'成分股：':^{self._width // 2 - 4}}"
            f"{' ' * (self._width // 2)}"
        )
        for constituent in self.constituents:
            self.print_row(
                f"{' ' * 2}"
                f"{f'{constituent.stock}':<{self._width - len(constituent.stock.name) - 10}}"
                f"{f'{round(100 * constituent.percent, 2)}%':<8}"
            )
