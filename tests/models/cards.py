from unittest import mock

import pytest

from monopoly.constants import CashType, TaxFee
from monopoly.models.boards import Board, BoardPlayer
from monopoly.models.equipments import cards as models
from monopoly.models.equipments.players import Player, PlayerLand
from monopoly.models.equipments.spaces import BaseSpace, StartPointSpace


class TestCashCard:
    @pytest.fixture(name="cash_earning_card")
    def fixture_cash_earning_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.CashCard:
        return cards[("CashCard", CashType.EARNING)]

    @pytest.fixture(name="cash_costing_card")
    def fixture_cash_costing_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.CashCard:
        return cards[("CashCard", CashType.COSTING)]

    def test_success_earning(
        self,
        board: Board,
        player: Player,
        cash_earning_card: models.CashCard,
    ):
        _cash = player.cash

        cash_earning_card.execute(player, board=board)

        assert player.cash == _cash + cash_earning_card.value
        assert player.incoming == cash_earning_card.value

    def test_success_costing(
        self,
        board: Board,
        player: Player,
        cash_costing_card: models.CashCard,
    ):
        _cash = player.cash

        cash_costing_card.execute(player, board=board)

        assert player.cash == _cash - cash_costing_card.value

    def test_failed_costing_bankruptcy(
        self,
        board: Board,
        player: Player,
        cash_costing_card: models.CashCard,
    ):
        cash_costing_card.value = (1 << 32) - 1

        with mock.patch("monopoly.models.equipments.players.input") as mock_input:
            _cash = player.cash

            cash_costing_card.execute(player, board=board)

            assert player.bankruptcy is True
            assert player.cash == _cash - cash_costing_card.value
            assert mock_input.call_count == 1


class TestCashChanceCard:
    @pytest.fixture(name="cash_chance_earning_card")
    def fixture_cash_chance_earning_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.CashChanceCard:
        return cards[("CashChanceCard", CashType.EARNING)]

    @pytest.fixture(name="cash_chance_costing_card")
    def fixture_cash_chance_costing_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.CashChanceCard:
        return cards[("CashChanceCard", CashType.COSTING)]

    def test_success_earning(
        self,
        board: Board,
        player: Player,
        cash_chance_earning_card: models.CashChanceCard,
    ):
        _cash = player.cash

        cash_chance_earning_card.execute(player, board=board)

        assert player.cash == _cash + cash_chance_earning_card.value
        assert player.incoming == cash_chance_earning_card.value

    def test_success_costing(
        self,
        board: Board,
        player: Player,
        cash_chance_costing_card: models.CashChanceCard,
    ):
        _cash = player.cash

        cash_chance_costing_card.execute(player, board=board)

        assert player.cash == _cash - cash_chance_costing_card.value

    def test_failed_costing_bankruptcy(
        self,
        board: Board,
        player: Player,
        cash_chance_costing_card: models.CashChanceCard,
    ):
        cash_chance_costing_card.value = (1 << 32) - 1

        with mock.patch("monopoly.models.equipments.players.input") as mock_input:
            _cash = player.cash

            cash_chance_costing_card.execute(player, board=board)

            assert player.bankruptcy is True
            assert player.cash == _cash - cash_chance_costing_card.value
            assert mock_input.call_count == 1


class TestForeclosePropertyCard:
    @pytest.fixture(name="foreclose_property_card")
    def fixture_foreclose_property_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.ForeclosePropertyCard:
        return cards[("ForeclosePropertyCard", None)]

    def test_success_buying(
        self,
        board: Board,
        player: Player,
        foreclose_property_card: models.ForeclosePropertyCard,
    ):
        new_land = board.lands["1002"]

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", new_land.id)):
            with mock.patch("monopoly.models.equipments.cards.input", return_value="y"):
                _cash = player.cash

                foreclose_property_card.execute(player, board=board)

                assert new_land.has_owner is True
                assert player.cash == _cash - int(new_land.land_price * TaxFee.FORECLOSE_FEE.value)
                assert new_land.stock.earning == int(new_land.land_price * new_land.stock.payout_ratio)
                assert player.lands[new_land.id].houses == 0
                assert board.credentials[new_land.id].houses == 0

    def test_success_construction(
        self,
        board: Board,
        player_land: PlayerLand,
        foreclose_property_card: models.ForeclosePropertyCard,
    ):
        player, land = player_land.player, player_land.land

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", land.id)):
            with mock.patch("monopoly.models.equipments.cards.input", return_value="y"):
                _cash = player.cash
                _houses = player_land.houses

                foreclose_property_card.execute(player, board=board)

                assert player_land.houses == _houses + 1
                assert player.cash == _cash - int(land.house_price * TaxFee.FORECLOSE_FEE.value)
                assert land.stock.earning == int(land.house_price * land.stock.payout_ratio)

    def test_success_cancelled(
        self,
        board: Board,
        player_land: PlayerLand,
        foreclose_property_card: models.ForeclosePropertyCard,
    ):
        new_land = board.lands["1002"]
        player, land = player_land.player, player_land.land

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", land.id, new_land.id, "c")):
            with mock.patch("monopoly.models.equipments.cards.input", return_value="n") as mock_card_input:
                _cash = player.cash
                _houses = player_land.houses

                foreclose_property_card.execute(player, board=board)

                assert player.cash == _cash
                assert new_land.has_owner is False
                assert player_land.houses == _houses
                assert land.stock.earning == 0
                assert new_land.stock.earning == 0
                with pytest.raises(KeyError):
                    assert player.lands[new_land.id]
                with pytest.raises(KeyError):
                    assert board.credentials[new_land.id]
                assert mock_card_input.call_count == 2

    def test_failed_non_foreclosable(
        self,
        board: Board,
        new_player: Player,
        player_ocean: PlayerLand,
        foreclose_property_card: models.ForeclosePropertyCard,
    ):
        new_land = board.lands["1002"]
        player, ocean = player_ocean.player, player_ocean.land

        new_land.has_owner = True
        credential = new_player.get_or_create_player_land(new_land)
        board.get_or_create_credential(new_land, credential=credential)

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", ocean.id, new_land.id, "c")):
            with mock.patch("monopoly.models.equipments.cards.input", return_value="y"):
                _cash = player.cash

                foreclose_property_card.execute(player, board=board)

                assert player.cash == _cash
                assert player_ocean.houses == 0
                assert new_land.stock.earning == 0
                with pytest.raises(KeyError):
                    assert player.lands[new_land.id]

    def test_failed_insufficient_cash(
        self,
        board: Board,
        player: Player,
        foreclose_property_card: models.ForeclosePropertyCard,
    ):
        new_land = board.lands["1002"]
        player.cash = 1

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", new_land.id, "c")):
            with mock.patch("monopoly.models.equipments.cards.input", return_value="y"):
                _cash = player.cash

                foreclose_property_card.execute(player, board=board)

                assert new_land.has_owner is False
                assert player.cash == _cash
                assert new_land.stock.earning == 0
                with pytest.raises(KeyError):
                    assert player.lands[new_land.id]
                with pytest.raises(KeyError):
                    assert board.credentials[new_land.id]


class TestFreeBuildingCard:
    @pytest.fixture(name="free_building_card")
    def fixture_free_building_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.FreeBuildingCard:
        return cards[("FreeBuildingCard", None)]

    def test_success(
        self,
        board: Board,
        player_land: PlayerLand,
        free_building_card: models.FreeBuildingCard,
    ):
        player, land = player_land.player, player_land.land

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", land.id)):
            _cash = player.cash
            _houses = player_land.houses

            free_building_card.execute(player, board=board)

            assert player.cash == _cash
            assert player_land.houses == _houses + 1
            assert land.stock.earning == int(land.house_price * land.stock.payout_ratio)

    def test_failed_buildable(
        self,
        board: Board,
        player_ocean: PlayerLand,
        free_building_card: models.FreeBuildingCard,
    ):
        player, ocean = player_ocean.player, player_ocean.land

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", ocean.id, "c")):
            _cash = player.cash

            free_building_card.execute(player, board=board)

            assert player.cash == _cash
            assert player_ocean.houses == 0


class TestFreeIncomingCard:
    @pytest.fixture(name="free_incoming_card")
    def fixture_free_incoming_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.FreeIncomingCard:
        return cards[("FreeIncomingCard", None)]

    def test_success(
        self,
        board: Board,
        player: Player,
        free_incoming_card: models.FreeIncomingCard,
    ):
        player.incoming = (1 << 32) - 1

        free_incoming_card.execute(player, board=board)

        assert player.incoming == 0


class TestFreeTollingCard:
    @pytest.fixture(name="free_tolling_card")
    def fixture_free_tolling_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.FreeTollingCard:
        return cards[("FreeTollingCard", None)]

    def test_success(
        self,
        board_player: BoardPlayer,
        free_tolling_card: models.FreeTollingCard,
    ):
        free_tolling_card.execute(board_player.player, board=board_player.board)
        assert board_player.can_free_tolling is True


class TestImposePropertyCard:
    @pytest.fixture(name="impose_property_card")
    def fixture_impose_property_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.ImposePropertyCard:
        return cards[("ImposePropertyCard", None)]

    def test_success(
        self,
        board: Board,
        new_player: Player,
        player_land: PlayerLand,
        impose_property_card: models.ImposePropertyCard,
    ):
        player, land = player_land.player, player_land.land

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", land.id)):
            with mock.patch("monopoly.models.equipments.cards.input", return_value="y"):
                _cash = player.cash
                _new_cash = new_player.cash
                _value = int(land.land_price * TaxFee.LEVY_FEE.value)

                impose_property_card.execute(new_player, board=board)

                assert player.cash == _cash + _value
                assert player.incoming == _value
                assert new_player.cash == _new_cash - _value
                assert new_player.get_or_create_player_land(land).houses == player_land.houses
                with pytest.raises(KeyError):
                    assert player.lands[land.id]
                assert board.get_or_create_credential(land).player == new_player

    def test_success_houses(
        self,
        board: Board,
        new_player: Player,
        player_land: PlayerLand,
        impose_property_card: models.ImposePropertyCard,
    ):
        player, land = player_land.player, player_land.land
        player_land.houses = 4
        new_player.cash = (1 << 32) - 1

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", land.id)):
            with mock.patch("monopoly.models.equipments.cards.input", return_value="y"):
                _cash = player.cash
                _new_cash = new_player.cash
                _value = int((land.land_price + 4 * land.house_price) * TaxFee.LEVY_FEE.value)

                impose_property_card.execute(new_player, board=board)

                assert player.cash == _cash + _value
                assert player.incoming == _value
                assert new_player.cash == _new_cash - _value
                assert new_player.get_or_create_player_land(land).houses == player_land.houses
                with pytest.raises(KeyError):
                    assert player.lands[land.id]
                assert board.get_or_create_credential(land).player == new_player

    def test_success_cancelled(
        self,
        board: Board,
        new_player: Player,
        player_land: PlayerLand,
        impose_property_card: models.ImposePropertyCard,
    ):
        player, land = player_land.player, player_land.land

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", land.id, "c")):
            with mock.patch("monopoly.models.equipments.cards.input", return_value="n"):
                _cash = player.cash
                _new_cash = new_player.cash

                impose_property_card.execute(new_player, board=board)

                assert player.cash == _cash
                assert player.incoming == 0
                assert new_player.cash == _new_cash
                assert player.get_or_create_player_land(land).houses == player_land.houses
                with pytest.raises(KeyError):
                    assert new_player.lands[land.id]
                assert board.get_or_create_credential(land).player == player

    def test_failed_non_imposable(
        self,
        board: Board,
        player_land: PlayerLand,
        impose_property_card: models.ImposePropertyCard,
    ):
        player, land = player_land.player, player_land.land

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", land.id, "c")):
            with mock.patch("monopoly.models.equipments.cards.input", return_value="y"):
                _cash = player.cash

                impose_property_card.execute(player, board=board)

                assert player.cash == _cash
                assert player.incoming == 0
                assert player.get_or_create_player_land(land).houses == player_land.houses
                assert board.get_or_create_credential(land).player == player

    def test_failed_insufficient_cash(
        self,
        board: Board,
        new_player: Player,
        player_land: PlayerLand,
        impose_property_card: models.ImposePropertyCard,
    ):
        player, land = player_land.player, player_land.land
        new_player.cash = 1

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", land.id, "c")):
            with mock.patch("monopoly.models.equipments.cards.input", return_value="y"):
                _cash = player.cash
                _new_cash = new_player.cash

                impose_property_card.execute(new_player, board=board)

                assert player.cash == _cash
                assert player.incoming == 0
                assert new_player.cash == _new_cash
                assert player.get_or_create_player_land(land).houses == player_land.houses
                with pytest.raises(KeyError):
                    assert new_player.lands[land.id]
                assert board.get_or_create_credential(land).player == player


class TestTransportStartPointCard:
    @pytest.fixture(name="trans_start_point_card")
    def fixture_trans_start_point_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.TransportStartPointCard:
        return cards[("TransportStartPointCard", None)]

    @pytest.fixture(name="start_point_space")
    def fixture_start_point_space(
        self,
        spaces: dict[str, BaseSpace],
    ) -> StartPointSpace:
        return spaces["STARTPOINT"]

    def test_success(
        self,
        board_player: BoardPlayer,
        trans_start_point_card: models.TransportStartPointCard,
        start_point_space: StartPointSpace,
    ):
        with mock.patch("monopoly.models.equipments.spaces.StartPointSpace.pass_by") as mock_pass_by:
            trans_start_point_card.execute(board_player.player, board=board_player.board)

            assert board_player.space.space == start_point_space
            assert mock_pass_by.call_count == 1


class TestHouseTaxCard:
    @pytest.fixture(name="house_tax_card")
    def fixture_house_tax_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.HouseTaxCard:
        return cards[("HouseTaxCard", None)]

    def test_success(
        self,
        board: Board,
        player: Player,
        house_tax_card: models.HouseTaxCard,
    ):
        _value = 1000

        with mock.patch("monopoly.models.equipments.players.Player.house_worth", new=_value):
            _cash = player.cash

            house_tax_card.execute(player, board=board)

            assert player.cash == _cash - int(_value * TaxFee.HOUSE_TAX.value)

    def test_failed_insufficient_cash(
        self,
        board: Board,
        player: Player,
        house_tax_card: models.HouseTaxCard,
    ):
        _value = (1 << 32) - 1

        with mock.patch("monopoly.models.equipments.players.Player.house_worth", new=_value):
            with mock.patch("monopoly.models.equipments.players.input") as mock_input:
                _cash = player.cash

                house_tax_card.execute(player, board=board)

                assert player.bankruptcy is True
                assert player.cash == _cash - int(_value * TaxFee.HOUSE_TAX.value)
                assert mock_input.call_count == 1


class TestIncomeTaxCard:
    @pytest.fixture(name="income_tax_card")
    def fixture_income_tax_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.IncomeTaxCard:
        return cards[("IncomeTaxCard", None)]

    def test_success(
        self,
        board: Board,
        player: Player,
        income_tax_card: models.IncomeTaxCard,
    ):
        player.incoming = 1000

        _cash = player.cash
        _incoming = player.incoming

        income_tax_card.execute(player, board=board)

        assert player.cash == _cash - int(_incoming * TaxFee.INCOMING_TAX.value)
        assert player.incoming == 0

    def test_failed_insufficient_cash(
        self,
        board: Board,
        player: Player,
        income_tax_card: models.IncomeTaxCard,
    ):
        player.incoming = (1 << 32) - 1

        with mock.patch("monopoly.models.equipments.players.input") as mock_input:
            _cash = player.cash
            _incoming = player.incoming

            income_tax_card.execute(player, board=board)

            assert player.bankruptcy is True
            assert player.cash == _cash - int(_incoming * TaxFee.INCOMING_TAX.value)
            assert player.incoming == 0
            assert mock_input.call_count == 1


class TestLandValueTaxCard:
    @pytest.fixture(name="land_value_tax_card")
    def fixture_land_value_tax_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.LandValueTaxCard:
        return cards[("LandValueTaxCard", None)]

    def test_success(
        self,
        board: Board,
        player: Player,
        land_value_tax_card: models.LandValueTaxCard,
    ):
        _value = 1000

        with mock.patch("monopoly.models.equipments.players.Player.land_worth", new=_value):
            _cash = player.cash

            land_value_tax_card.execute(player, board=board)

            assert player.cash == _cash - int(_value * TaxFee.LAND_VALUE_TAX.value)

    def test_failed_insufficient_cash(
        self,
        board: Board,
        player: Player,
        land_value_tax_card: models.LandValueTaxCard,
    ):
        _value = (1 << 32) - 1

        with mock.patch("monopoly.models.equipments.players.Player.land_worth", new=_value):
            with mock.patch("monopoly.models.equipments.players.input") as mock_input:
                _cash = player.cash

                land_value_tax_card.execute(player, board=board)

                assert player.bankruptcy is True
                assert player.cash == _cash - int(_value * TaxFee.LAND_VALUE_TAX.value)
                assert mock_input.call_count == 1


class TestStockHandlingFeeCard:
    @pytest.fixture(name="stock_handling_fee_card")
    def fixture_stock_handling_fee_card(
        self,
        cards: dict[tuple, models.BaseCard],
    ) -> models.StockHandlingFeeCard:
        return cards[("StockHandlingFeeCard", None)]

    def test_success(
        self,
        board: Board,
        player: Player,
        stock_handling_fee_card: models.StockHandlingFeeCard,
    ):
        _value = 1000

        with mock.patch("monopoly.models.equipments.players.Player.stock_worth", new=_value):
            _cash = player.cash

            stock_handling_fee_card.execute(player, board=board)

            assert player.cash == _cash - int(_value * TaxFee.STOCK_HANDLING_FEE.value)

    def test_failed_insufficient_cash(
        self,
        board: Board,
        player: Player,
        stock_handling_fee_card: models.StockHandlingFeeCard,
    ):
        _value = (1 << 32) - 1

        with mock.patch("monopoly.models.equipments.players.Player.stock_worth", new=_value):
            with mock.patch("monopoly.models.equipments.players.input") as mock_input:
                _cash = player.cash

                stock_handling_fee_card.execute(player, board=board)

                assert player.bankruptcy is True
                assert player.cash == _cash - int(_value * TaxFee.STOCK_HANDLING_FEE.value)
                assert mock_input.call_count == 1
