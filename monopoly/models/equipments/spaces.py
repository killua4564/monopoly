import abc
import random

import pydantic

from monopoly import configs
from monopoly.constants import CardType, CashType, SystemText

from ..properties import BaseLand


class BaseSpace(pydantic.BaseModel, abc.ABC):
    id: str
    name: str
    moving_point: int = pydantic.Field(1, ge=1)

    @abc.abstractmethod
    def arrive(self, player: "BasePlayer", **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def pass_by(self, player: "BasePlayer", **kwargs):
        raise NotImplementedError

    def __eq__(self, other: "BaseSpace") -> bool:
        return self.id == other.id

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.name


class CardSpace(BaseSpace):
    name: CardType

    def arrive(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 抽取 {self.name.value} 一張")
        input(SystemText.PRESS_ENTER_TO_CONTINUE.value)
        random.choice(board.cards[self.name]).execute(player, board=board)
        input(SystemText.PRESS_ENTER_TO_CONTINUE.value)

    def pass_by(self, player: "BasePlayer", **kwargs):
        pass


class CashSpace(BaseSpace):
    name: CashType
    value: int = configs.CASH_SPACE_VALUE

    def arrive(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} {self.name.value} ${self.value}")
        if self.name == CashType.EARNING:
            player.earn(self.value)
        elif self.name == CashType.COSTING:
            player.prepare_payment(board, self.value, force=True)
            player.pay(self.value)
        input(SystemText.PRESS_ENTER_TO_CONTINUE.value)

    def pass_by(self, player: "BasePlayer", **kwargs):
        pass


class LandSpace(BaseSpace):
    land: BaseLand

    def arrive(self, player: "BasePlayer", *, board: "Board", **kwargs):
        if not self.land.has_owner:
            self.land.buy(player, board)
            return

        credential = board.get_or_create_credential(self.land)
        if credential.player != player:
            credential.tolling(player, board)
            return

        if self.land.buildable:
            credential.construct(board)

    def pass_by(self, player: "BasePlayer", **kwargs):
        pass


class PausePlayerSpace(BaseSpace):
    name: str = SystemText.PAUSE_SPACE_NAME.value
    value: int = 1

    def arrive(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 下回合暫停乙次")
        board.pause(player, self.value)
        input(SystemText.PRESS_ENTER_TO_CONTINUE.value)

    def pass_by(self, player: "BasePlayer", **kwargs):
        pass


class StartPointSpace(BaseSpace):
    name: str = SystemText.START_POINT_NAME.value
    value: int = configs.PASS_START_POINT_CASH

    def arrive(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 抵達起點可選擇是否要反轉一切的方向 (Y/N)")
        if input("> ").upper() == "Y":
            board.reverse_direction()
            print(SystemText.REVERSE_FINISH.value)
            input(SystemText.PRESS_ENTER_TO_CONTINUE.value)

    def pass_by(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 經過起點獲得 ${self.value} 和購買股票的權利")
        player.earn(self.value)
        board.buy_stock(player)


class ThreeDicesSpace(BaseSpace):
    name: str = SystemText.THREE_DICES_NAME.value

    def arrive(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 得到擲三顆骰子的機會")
        board.set_three_dices(player)
        input(SystemText.PRESS_ENTER_TO_CONTINUE.value)

    def pass_by(self, player: "BasePlayer", **kwargs):
        pass


class TransportStartPointSpace(BaseSpace):
    name: str = SystemText.TRANSPORT_START_POINT_NAME.value

    def arrive(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 是否要傳送到起點？(Y/N)")
        if input("> ").upper() == "Y":
            print(SystemText.TRANSPORT_FINISH.value)
            board.transport_start_point(player, as_arrive=True)

    def pass_by(self, player: "BasePlayer", **kwargs):
        pass
