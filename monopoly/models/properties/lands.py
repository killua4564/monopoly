import abc
import contextlib
import typing

import pydantic

from monopoly import configs
from monopoly.constants import Area, SystemText

from ..interfaces import TradableMenuInterface


class BaseLand(TradableMenuInterface, abc.ABC):
    id: str
    name: str
    area: Area
    land_price: int = pydantic.Field(..., ge=0)
    tolls: tuple[int, ...]

    buildable: bool = True
    has_owner: bool = False

    @pydantic.validator("tolls")
    def validate_tolls(cls, tolls: tuple[int, ...]):
        if any(toll < 0 for toll in tolls):
            raise ValueError("Invalid tolls")
        return tolls

    @property
    def sale_value(self) -> int:
        return int(self.land_price * configs.LAND_DISCOUNT_RATE)

    def buy(self, player: "BasePlayer", board: "Board"):
        with contextlib.suppress(self.Cancelled):
            while not self.has_owner:
                self.buy_menu(player, board)

    def buying(
        self,
        player: "BasePlayer",
        board: "Board",
        *,
        is_free: bool = False,
    ):
        assert not self.has_owner
        if not is_free:
            if not player.prepare_payment(board, self.land_price):
                return

            player.pay(self.land_price)

        credential = player.get_or_create_player_land(self)
        board.get_or_create_credential(self, credential=credential)
        self.has_owner = True
        print(SystemText.BUYING_SUCCESS.value)

    def sell(self, player: "BasePlayer", board: "Board"):
        with contextlib.suppress(self.Cancelled):
            while self.has_owner and board.get_or_create_credential(self).player == player:
                self.sell_menu(player, board)

    def selling(
        self,
        player: "BasePlayer",
        board: "Board",
        *,
        silent: bool = False,
    ):
        assert board.get_or_create_credential(self).player == player
        player.earn(self.sale_value, income_tax_free=True)
        player.delete_or_skip_player_land(self)
        board.delete_or_skip_credential(self)
        self.has_owner = False
        if not silent:
            print(SystemText.SELLING_SUCCESS.value)

    def show(self, **kwargs):
        self.show_divider()
        self.show_base_info()
        self.show_horizontal()
        self.show_land_info(**kwargs)
        self.show_horizontal()
        self.show_tolling_info()
        self.show_divider()

    def show_base_info(self):
        self.print_row(
            f"{self.id:^{self._width // 2}}"
            f"{self.name:^{self._width // 2 - len(self.name)}}"
        )

    def show_land_info(self, **kwargs):
        self.print_row(
            f"{'區域：':>{self._width // 2 - 3}}"
            f"{self.area.value:<{self._width // 2}}"
        )
        self.print_row(
            f"{'土地價值：':>{self._width // 2 - 5}}"
            f"{f'${self.land_price}':<{self._width // 2}}"
        )

    @abc.abstractmethod
    def show_tolling_info(self):
        raise NotImplementedError

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return f"{self.id} {self.name}"


class Land(BaseLand):
    house_price: int = pydantic.Field(..., ge=0)
    tolls: tuple[int, int, int, int, int]

    stock: typing.Union["Stock", None] = None

    def buying(
        self,
        player: "BasePlayer",
        board: "Board",
        *,
        is_free: bool = False,
    ):
        super().buying(player, board, is_free=is_free)
        if self.has_owner:
            with contextlib.suppress(AttributeError):
                self.stock.earn(self.land_price)
            if configs.UNLIMITED_BUILDING and not is_free:
                board.get_or_create_credential(self).construct(board)

    def selling(
        self,
        player: "BasePlayer",
        board: "Board",
        *,
        silent: bool = False,
    ):
        super().selling(player, board, silent=silent)
        with contextlib.suppress(AttributeError):
            self.stock.pay(self.sale_value)

    def show_land_info(self, houses: int = 0):
        super().show_land_info()
        self.print_row(
            f"{'房屋價值：':>{self._width // 2 - 5}}"
            f"{f'${self.house_price}':<{self._width // 2}}"
        )
        self.print_row(
            f"{'房屋數量：':>{self._width // 2 - 5}}"
            f"{houses:<{self._width // 2}}"
        )

    def show_tolling_info(self):
        self.print_row(
            f"{'過路費：':^{self._width // 2 - 4}}"
            f"{' ' * (self._width // 2)}"
        )
        for idx, toll in enumerate(self.tolls):
            self.print_row(
                f"{f'{idx}棟房屋：':>{self._width // 2 - 4}}"
                f"{f'${toll}':<{self._width // 2}}"
            )


class Ocean(BaseLand):
    area: Area = Area.OCEAN
    tolls: tuple[int]

    buildable: bool = False

    def show_tolling_info(self):
        self.print_row(
            f"{'過路費：':>{self._width // 2 - 4}}"
            f"{f'${self.tolls[0]}':<{self._width // 2}}"
        )
