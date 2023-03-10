import abc
import contextlib

import pydantic

from monopoly.constants import CardType, CashType, SystemText, TaxFee


class BaseCard(pydantic.BaseModel, abc.ABC):
    card_type: CardType

    @abc.abstractmethod
    def execute(self, player: "BasePlayer", **kwargs):
        raise NotImplementedError


class CashCard(BaseCard):
    cash_type: CashType
    value: int = 1000

    def execute(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 抽到 {self.cash_type.value} ${self.value}")
        if self.cash_type == CashType.EARNING:
            player.earn(self.value)
        elif self.cash_type == CashType.COSTING:
            player.prepare_payment(board, self.value, force=True)
            player.pay(self.value)


class CashChanceCard(BaseCard):
    card_type: CardType = CardType.CHANCE

    value: int = 1000
    cash_type: CashType

    @property
    def detail(self) -> str:
        if self.cash_type == CashType.EARNING:
            return "最少"
        if self.cash_type == CashType.COSTING:
            return "最多"
        raise ValueError(f"Unknown CashType {self.cash_type}")

    def execute(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 抽到存款 {self.detail} 的玩家 {self.cash_type.value} ${self.value}")
        if self.cash_type == CashType.EARNING:
            player = board.poorest_player
            player.earn(self.value)
        elif self.cash_type == CashType.COSTING:
            player = board.richest_player
            player.prepare_payment(board, self.value, force=True)
            player.pay(self.value)
        print(f"{player} {self.cash_type.value} ${self.value}")


class ForeclosePropertyCard(BaseCard):
    card_type: CardType = CardType.CHANCE

    def _execute_logic(self, player: "BasePlayer", board: "Board"):
        print(f"{player} 想要查看哪個的不動產呢？")
        board.list_lands()

        try:
            land = board.lands[board.cancelable_command]
        except KeyError:
            print(SystemText.PROPERTY_CODE_ERROR.value)
            return

        value = int(land.land_price * TaxFee.FORECLOSE_FEE.value)
        with contextlib.suppress(AssertionError):
            credential = board.get_or_create_credential(land)
            if not (credential.player == player and land.buildable):
                print("此不動產不得法拍")
                return

            value = int(land.house_price * TaxFee.FORECLOSE_FEE.value)

        print(f"{player} 需要支付 {land} 的法拍費 ${value} 向銀行購買 (Y/N)")
        if input("> ").upper() == "Y" and player.prepare_payment(board, value):
            player.pay(value)
            if not land.has_owner:
                land.buying(player, board, is_free=True)
            else:
                credential = board.get_or_create_credential(land)
                credential.construction(board, is_free=True)

            raise board.Cancelled()

    def execute(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 抽到可向銀行購買法拍不動產!!(買入價值 {int(100 * TaxFee.FORECLOSE_FEE.value)}%)")
        with contextlib.suppress(board.Cancelled):
            while True:
                self._execute_logic(player, board)


class FreeBuildingCard(BaseCard):
    card_type: CardType = CardType.COMMUNITY_CHEST

    def _execute_logic(self, player: "BasePlayer", board: "Board"):
        print(f"{player} 想要在哪片土地建房屋呢？")
        player.list_lands()

        try:
            credential = player.lands[player.cancelable_command]
            credential.construction(board, is_free=True)
            raise player.Cancelled()
        except AssertionError:
            print("此土地不能建房屋了!!")
        except KeyError:
            print(SystemText.PROPERTY_CODE_ERROR.value)

    def execute(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 抽到免費建房屋乙棟!!")
        with contextlib.suppress(player.Cancelled):
            while True:
                self._execute_logic(player, board)


class FreeIncomingCard(BaseCard):
    card_type: CardType = CardType.COMMUNITY_CHEST

    def execute(self, player: "BasePlayer", **kwargs):
        print(f"{player} 抽到免繳所得稅乙次!!")
        player.incoming = 0


class FreeTollingCard(BaseCard):
    card_type: CardType = CardType.CHANCE

    def execute(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 抽到免付過路費!!")
        board.set_free_tolling(player)


class ImposePropertyCard(BaseCard):
    card_type: CardType = CardType.CHANCE

    def _execute_logic(self, player: "BasePlayer", board: "Board"):
        print(f"{player} 想要查看哪個的不動產呢？")
        board.list_lands()

        try:
            land = board.lands[board.cancelable_command]
        except KeyError:
            print(SystemText.PROPERTY_CODE_ERROR.value)
            return

        try:
            credential = board.get_or_create_credential(land)
            assert credential.player != player
        except AssertionError:
            print("此不動產不得徵收!!")
            return

        owner = credential.player
        value = int(credential.worth * TaxFee.IMPOSE_FEE.value)
        print(f"{player} 需要支付 {land} 的徵收費 ${value} 給 {owner} (Y/N)")
        if input("> ").upper() == "Y" and player.prepare_payment(board, value):
            player.pay(value)
            owner.earn(value)

            # delete owner credential
            owner.delete_or_skip_player_land(land)
            board.delete_or_skip_credential(land)

            # create player credential
            credential = player.get_or_create_player_land(land, houses=credential.houses)
            board.get_or_create_credential(land, credential=credential)

            raise board.Cancelled()

    def execute(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 抽到可向玩家徵收不動產!!(買入總價值 {int(100 * TaxFee.IMPOSE_FEE.value)}%)")
        with contextlib.suppress(board.Cancelled):
            while True:
                self._execute_logic(player, board)


class ReturnToStartPointCard(BaseCard):
    card_type: CardType = CardType.CHANCE

    def execute(self, player: "BasePlayer", *, board: "Board", **kwargs):
        print(f"{player} 抽到返回起點!!")
        board.transport_start_point(player)


class BasePayingCard(BaseCard, abc.ABC):
    card_type: CardType = CardType.COMMUNITY_CHEST

    name: str
    detail: str

    def pay(self, player: "BasePlayer", board: "Board", value: int):
        print(f"{player} 抽到需繳交 {self.name} ${value} ({self.detail})")
        player.prepare_payment(board, value, force=True)
        player.pay(value)


class HouseTaxCard(BasePayingCard):
    name: str = "房屋稅"
    detail: str = f"房屋價值總額 {int(100 * TaxFee.HOUSE_TAX.value)}%"

    def execute(self, player: "BasePlayer", *, board: "Board", **kwargs):
        self.pay(
            player,
            board,
            int(player.house_worth * TaxFee.HOUSE_TAX.value),
        )


class IncomeTaxCard(BasePayingCard):
    name: str = "所得稅"
    detail: str = f"累積所得總額 {int(100 * TaxFee.INCOMING_TAX.value)}%"

    def execute(self, player: "BasePlayer", *, board: "Board", **kwargs):
        self.pay(
            player,
            board,
            int(player.incoming * TaxFee.INCOMING_TAX.value),
        )
        player.incoming = 0


class LandValueTaxCard(BasePayingCard):
    name: str = "地價稅"
    detail: str = f"土地價值總額 {int(100 * TaxFee.LAND_VALUE_TAX.value)}%"

    def execute(self, player: "BasePlayer", *, board: "Board", **kwargs):
        self.pay(
            player,
            board,
            int(player.land_worth * TaxFee.LAND_VALUE_TAX.value),
        )


class StockHandlingFeeCard(BasePayingCard):
    name: str = "股票交易手續費"
    detail: str = f"股票總額 {round(100 * TaxFee.STOCK_HANDLING_FEE.value, 4)}%"

    def execute(self, player: "BasePlayer", *, board: "Board", **kwargs):
        self.pay(
            player,
            board,
            int(player.stock_worth * TaxFee.STOCK_HANDLING_FEE.value),
        )
