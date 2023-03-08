from unittest import mock

import pytest

from monopoly.models.boards import Board
from monopoly.models.equipments.players import Player, PlayerLand
from monopoly.models.properties.lands import Land, Ocean


class TestBuyingLand:
    def test_success(self, board: Board, player: Player, land: Land):
        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b")):
            with mock.patch("monopoly.models.equipments.players.PlayerLand.construct") as mock_construct:
                with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=False):
                    _cash = player.cash

                    land.buy(player, board)

                    assert land.has_owner is True
                    assert player.cash == _cash - land.land_price
                    assert land.stock.earning == int(land.land_price * land.stock.payout_ratio)
                    assert player.lands[land.id].houses == 0
                    assert board.credentials[land.id].houses == 0
                    assert mock_construct.call_count == 0

    def test_success_unlimited(self, board: Board, player: Player, land: Land):
        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b")):
            with mock.patch("monopoly.models.equipments.players.PlayerLand.construct") as mock_construct:
                with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=True):
                    _cash = player.cash

                    land.buy(player, board)

                    assert land.has_owner is True
                    assert player.cash == _cash - land.land_price
                    assert land.stock.earning == int(land.land_price * land.stock.payout_ratio)
                    assert player.lands[land.id].houses == 0
                    assert board.credentials[land.id].houses == 0
                    assert mock_construct.call_count == 1

    def test_success_opening(self, board: Board, player: Player, land: Land):
        for _ in range(10):
            board.opening_stocks()

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b")):
            with mock.patch("monopoly.models.equipments.players.PlayerLand.construct") as mock_construct:
                with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=True):
                    _cash = player.cash

                    land.buy(player, board)

                    assert land.has_owner is True
                    assert player.cash == _cash - land.land_price
                    assert land.stock.earning == int(land.land_price * land.stock.payout_ratio)
                    assert player.lands[land.id].houses == 0
                    assert board.credentials[land.id].houses == 0
                    assert mock_construct.call_count == 1

    def test_success_is_free(self, board: Board, player: Player, land: Land):
        with mock.patch("monopoly.models.equipments.players.PlayerLand.construct") as mock_construct:
            with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=True):
                _cash = player.cash

                land.buying(player, board, is_free=True)

                assert land.has_owner is True
                assert player.cash == _cash
                assert land.stock.earning == int(land.land_price * land.stock.payout_ratio)
                assert player.lands[land.id].houses == 0
                assert board.credentials[land.id].houses == 0
                assert mock_construct.call_count == 0

    def test_failed_insufficient_cash(self, board: Board, player: Player, land: Land):
        player.cash = 1

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "c")):
            _cash = player.cash

            land.buy(player, board)

            assert land.has_owner is False
            assert player.cash == _cash
            assert land.stock.earning == 0
            with pytest.raises(KeyError):
                assert player.lands[land.id]
            with pytest.raises(KeyError):
                assert board.credentials[land.id]

    def test_failed_has_owner(self, board: Board, player: Player, land: Land):
        land.has_owner = True

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b")):
            _cash = player.cash

            land.buy(player, board)

            assert land.has_owner is True
            assert player.cash == _cash
            assert land.stock.earning == 0
            with pytest.raises(KeyError):
                assert player.lands[land.id]


class TestBuyingOcean:
    def test_success(self, board: Board, player: Player, ocean: Ocean):
        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b")):
            _cash = player.cash

            ocean.buy(player, board)

            assert ocean.has_owner is True
            assert player.cash == _cash - ocean.land_price
            assert player.lands[ocean.id].houses == 0
            assert board.credentials[ocean.id].houses == 0

    def test_success_is_free(self, board: Board, player: Player, ocean: Ocean):
        _cash = player.cash

        ocean.buying(player, board, is_free=True)

        assert ocean.has_owner is True
        assert player.cash == _cash
        assert player.lands[ocean.id].houses == 0
        assert board.credentials[ocean.id].houses == 0

    def test_failed_insufficient_cash(self, board: Board, player: Player, ocean: Ocean):
        player.cash = 1

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "c")):
            _cash = player.cash

            ocean.buy(player, board)

            assert ocean.has_owner is False
            assert player.cash == _cash
            with pytest.raises(KeyError):
                assert player.lands[ocean.id]
            with pytest.raises(KeyError):
                assert board.credentials[ocean.id]

    def test_failed_has_owner(self, board: Board, player: Player, ocean: Ocean):
        ocean.has_owner = True

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b")):
            _cash = player.cash

            ocean.buy(player, board)

            assert ocean.has_owner is True
            assert player.cash == _cash
            with pytest.raises(KeyError):
                assert player.lands[ocean.id]


class TestSellingLand:
    def test_success(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s")):
            _cash = player.cash

            land.sell(player, board)

            assert land.has_owner is False
            assert player.cash == _cash + land.sale_value
            assert land.stock.payment == int(land.sale_value * land.stock.payout_ratio)
            assert player.incoming == 0
            with pytest.raises(KeyError):
                assert player.lands[land.id]
            with pytest.raises(KeyError):
                assert board.credentials[land.id]

    def test_success_opening(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land
        for _ in range(10):
            board.opening_stocks()

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s")):
            _cash = player.cash

            land.sell(player, board)

            assert land.has_owner is False
            assert player.cash == _cash + land.sale_value
            assert land.stock.payment == int(land.sale_value * land.stock.payout_ratio)
            assert player.incoming == 0
            with pytest.raises(KeyError):
                assert player.lands[land.id]
            with pytest.raises(KeyError):
                assert board.credentials[land.id]

    def test_success_silent(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land

        with mock.patch("monopoly.models.properties.lands.print") as mock_print:
            _cash = player.cash

            land.selling(player, board, silent=True)

            assert land.has_owner is False
            assert player.cash == _cash + land.sale_value
            assert land.stock.payment == int(land.sale_value * land.stock.payout_ratio)
            assert player.incoming == 0
            with pytest.raises(KeyError):
                assert player.lands[land.id]
            with pytest.raises(KeyError):
                assert board.credentials[land.id]
            assert mock_print.call_count == 0

    def test_failed_has_owner(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land
        land.has_owner = False

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s")):
            _cash = player.cash

            land.sell(player, board)

            assert land.has_owner is False
            assert player.cash == _cash
            assert land.stock.payment == 0
            assert player.incoming == 0

    def test_failed_credential_player(self, board: Board, player_land: PlayerLand, new_player: Player):
        player, land = player_land.player, player_land.land
        player_land.player = new_player

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s")):
            _cash = player.cash

            land.sell(player, board)

            assert land.has_owner is True
            assert player.cash == _cash
            assert land.stock.payment == 0
            assert player.incoming == 0


class TestSellingOcean:
    def test_success(self, board: Board, player_ocean: PlayerLand):
        player, ocean = player_ocean.player, player_ocean.land

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s")):
            _cash = player.cash

            ocean.sell(player, board)

            assert ocean.has_owner is False
            assert player.cash == _cash + ocean.sale_value
            assert player.incoming == 0
            with pytest.raises(KeyError):
                assert player.lands[ocean.id]
            with pytest.raises(KeyError):
                assert board.credentials[ocean.id]

    def test_success_silent(self, board: Board, player_ocean: PlayerLand):
        player, ocean = player_ocean.player, player_ocean.land

        with mock.patch("monopoly.models.properties.lands.print") as mock_print:
            _cash = player.cash

            ocean.selling(player, board, silent=True)

            assert ocean.has_owner is False
            assert player.cash == _cash + ocean.sale_value
            assert player.incoming == 0
            with pytest.raises(KeyError):
                assert player.lands[ocean.id]
            with pytest.raises(KeyError):
                assert board.credentials[ocean.id]
            assert mock_print.call_count == 0

    def test_failed_has_owner(self, board: Board, player_ocean: PlayerLand):
        player, ocean = player_ocean.player, player_ocean.land
        ocean.has_owner = False

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s")):
            _cash = player.cash

            ocean.sell(player, board)

            assert ocean.has_owner is False
            assert player.cash == _cash
            assert player.incoming == 0

    def test_failed_credential_player(self, board: Board, player_ocean: PlayerLand, new_player: Player):
        player, ocean = player_ocean.player, player_ocean.land
        player_ocean.player = new_player

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s")):
            _cash = player.cash

            ocean.sell(player, board)

            assert ocean.has_owner is True
            assert player.cash == _cash
            assert player.incoming == 0


class TestConstructionLand:
    def test_success(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b")):
            with mock.patch("monopoly.models.equipments.players.configs.BUILDING_UPPERBOUND", new=4):
                with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=False):
                    _cash = player.cash
                    _houses = player_land.houses

                    player_land.construct(board)

                    assert player_land.houses == _houses + 1
                    assert player.cash == _cash - land.house_price
                    assert land.stock.earning == int(land.house_price * land.stock.payout_ratio)

    def test_success_unlimited(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land
        player.cash = (1 << 32) - 1

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "b", "c")):
            with mock.patch("monopoly.models.equipments.players.configs.BUILDING_UPPERBOUND", new=4):
                with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=True):
                    _cash = player.cash
                    _houses = player_land.houses

                    player_land.construct(board)

                    assert player_land.houses == _houses + 2
                    assert player.cash == _cash - 2 * land.house_price
                    assert land.stock.earning == 2 * int(land.house_price * land.stock.payout_ratio)

    def test_success_opening(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land
        for _ in range(10):
            board.opening_stocks()

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "c")):
            with mock.patch("monopoly.models.equipments.players.configs.BUILDING_UPPERBOUND", new=4):
                with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=True):
                    _cash = player.cash
                    _houses = player_land.houses

                    player_land.construct(board)

                    assert player_land.houses == _houses + 1
                    assert player.cash == _cash - land.house_price
                    assert land.stock.earning == int(land.house_price * land.stock.payout_ratio)

    def test_success_is_free(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land

        with mock.patch("monopoly.models.equipments.players.configs.BUILDING_UPPERBOUND", new=4):
            with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=True):
                _cash = player.cash
                _houses = player_land.houses

                player_land.construction(board, is_free=True)

                assert player_land.houses == _houses + 1
                assert player.cash == _cash
                assert land.stock.earning == int(land.house_price * land.stock.payout_ratio)

    def test_failed_insufficient_cash(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land
        land.house_price = (1 << 32) - 1

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "c")):
            _cash = player.cash
            _houses = player_land.houses

            player_land.construct(board)

            assert player_land.houses == _houses
            assert player.cash == _cash
            assert land.stock.earning == 0

    def test_failed_trade_off(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land
        player.cash = 1

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "l", "i", "m", "s", "c")):
            with mock.patch("monopoly.models.interfaces.lists.input", side_effect=(land.id, "c")):
                _cash = player.cash
                _houses = player_land.houses

                player_land.construct(board)

                assert player_land.houses == _houses
                assert player.cash == _cash + land.sale_value
                assert player.incoming == 0
                assert land.stock.payment == int(land.sale_value * land.stock.payout_ratio)
                with pytest.raises(KeyError):
                    assert player.lands[land.id]
                with pytest.raises(KeyError):
                    assert board.credentials[land.id]

    def test_failed_upperbound(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land
        player_land.houses = 4

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b")):
            with mock.patch("monopoly.models.equipments.players.configs.BUILDING_UPPERBOUND", new=4):
                with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=False):
                    _cash = player.cash
                    _houses = player_land.houses

                    player_land.construct(board)

                    assert player_land.houses == _houses
                    assert player.cash == _cash
                    assert land.stock.earning == 0


class TestConstructionOcean:
    def test_failed_buildable(self, board: Board, player_ocean: PlayerLand):
        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b")):
            with mock.patch("monopoly.models.equipments.players.configs.BUILDING_UPPERBOUND", new=4):
                with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=False):
                    _cash = player_ocean.player.cash

                    with pytest.raises(AssertionError):
                        player_ocean.construct(board)

                    assert player_ocean.houses == 0
                    assert player_ocean.player.cash == _cash


class TestDemolitionLand:
    def test_success(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land
        player_land.houses = 2

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "d", "c")):
            _cash = player.cash
            _houses = player_land.houses

            player_land.demolish(board)

            assert player_land.houses == _houses - 1
            assert player.cash == _cash + player_land.sale_value
            assert player.incoming == 0
            assert land.stock.payment == int(player_land.sale_value * land.stock.payout_ratio)

    def test_success_twice(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land
        player_land.houses = 3

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "d", "d", "c")):
            _cash = player.cash
            _houses = player_land.houses

            player_land.demolish(board)

            assert player_land.houses == _houses - 2
            assert player.cash == _cash + 2 * player_land.sale_value
            assert player.incoming == 0
            assert land.stock.payment == 2 * int(player_land.sale_value * land.stock.payout_ratio)

    def test_success_opening(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land
        player_land.houses = 2
        for _ in range(10):
            board.opening_stocks()

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "d", "c")):
            _cash = player.cash
            _houses = player_land.houses

            player_land.demolish(board)

            assert player_land.houses == _houses - 1
            assert player.cash == _cash + player_land.sale_value
            assert player.incoming == 0
            assert land.stock.payment == int(player_land.sale_value * land.stock.payout_ratio)

    def test_success_silent(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land
        player_land.houses = 1

        with mock.patch("monopoly.models.equipments.players.print") as mock_print:
            _cash = player.cash
            _houses = player_land.houses

            player_land.demolition(board, silent=True)

            assert player_land.houses == _houses - 1
            assert player.cash == _cash + player_land.sale_value
            assert player.incoming == 0
            assert land.stock.payment == int(player_land.sale_value * land.stock.payout_ratio)
            assert mock_print.call_count == 0

    def test_failed_houses(self, board: Board, player_land: PlayerLand):
        player, land = player_land.player, player_land.land
        player_land.houses = 0

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "d", "c")):
            _cash = player.cash
            _houses = player_land.houses

            player_land.demolish(board)

            assert player_land.houses == _houses
            assert player.cash == _cash
            assert player.incoming == 0
            assert land.stock.payment == 0


class TestDemolitionOcean:
    def test_failed_buildable(self, board: Board, player_ocean: PlayerLand):
        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "d")):
            _cash = player_ocean.player.cash

            with pytest.raises(AssertionError):
                player_ocean.demolish(board)

            assert player_ocean.houses == 0
            assert player_ocean.player.cash == _cash
