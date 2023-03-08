from unittest import mock

from monopoly.models.boards import Board
from monopoly.models.equipments.players import Player, PlayerLand, PlayerStock


class TestPlayerBankrupt:
    def test_success(
        self,
        board: Board,
        player_land: PlayerLand,
        player_stock: PlayerStock,
    ):
        player_land.houses = 1
        player, land, stock = player_land.player, player_land.land, player_stock.stock

        _cash = player.cash

        player.bankrupt(board)

        assert player.bankruptcy is True
        assert player.cash == (
            _cash + land.sale_value + player_land.sale_value + stock.sale_value
        )


class TestPlayerPreparePayment:
    def test_success(
        self,
        board: Board,
        player: Player,
    ):
        with mock.patch("monopoly.models.equipments.players.Player.bankrupt") as mock_bankrupt:
            with mock.patch("monopoly.models.equipments.players.input") as mock_input:
                _cash = player.cash

                assert player.prepare_payment(board, _cash - 1) is True
                assert player.cash == _cash
                assert mock_input.call_count == 0
            assert mock_bankrupt.call_count == 0

    def test_success_force(
        self,
        board: Board,
        player: Player,
    ):
        with mock.patch("monopoly.models.equipments.players.Player.bankrupt") as mock_bankrupt:
            with mock.patch("monopoly.models.equipments.players.input") as mock_input:
                _cash = player.cash

                assert player.prepare_payment(board, _cash - 1, force=True) is True
                assert player.cash == _cash
                assert mock_input.call_count == 0
            assert mock_bankrupt.call_count == 0

    def test_success_prepared(
        self,
        board: Board,
        player_land: PlayerLand,
        player_stock: PlayerStock,
    ):
        player_land.houses = 1
        player, land, stock = player_land.player, player_land.land, player_stock.stock

        with mock.patch("monopoly.models.equipments.players.Player.bankrupt") as mock_bankrupt:
            with mock.patch("monopoly.models.equipments.players.input") as mock_input:
                with mock.patch(
                    "monopoly.models.interfaces.menus.input",
                    side_effect=("l", "d", "l", "s", "s", "s", "c"),
                ):
                    with mock.patch(
                        "monopoly.models.interfaces.lists.input",
                        side_effect=("0000", land.id, "c", land.id, "c", stock.id, "c"),
                    ):
                        _value = player.cash + land.sale_value + stock.sale_value + player_land.sale_value

                        assert player.prepare_payment(board, _value) is True
                        assert player.cash == _value
                assert mock_input.call_count == 0
            assert mock_bankrupt.call_count == 0

    def test_success_prepared_cancelled(
        self,
        board: Board,
        player_land: PlayerLand,
        player_stock: PlayerStock,
    ):
        player_land.houses = 1
        player, land, stock = player_land.player, player_land.land, player_stock.stock

        with mock.patch("monopoly.models.equipments.players.Player.bankrupt") as mock_bankrupt:
            with mock.patch("monopoly.models.equipments.players.input") as mock_input:
                with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("c",)):
                    _cash = player.cash
                    _value = _cash + land.sale_value + stock.sale_value + player_land.sale_value

                    assert player.prepare_payment(board, _value) is False
                    assert player.cash == _cash
                assert mock_input.call_count == 0
            assert mock_bankrupt.call_count == 0

    def test_success_prepared_force(
        self,
        board: Board,
        player_land: PlayerLand,
        player_stock: PlayerStock,
    ):
        player_land.houses = 1
        player, land, stock = player_land.player, player_land.land, player_stock.stock

        with mock.patch("monopoly.models.equipments.players.Player.bankrupt") as mock_bankrupt:
            with mock.patch("monopoly.models.equipments.players.input") as mock_input:
                with mock.patch(
                    "monopoly.models.interfaces.menus.input",
                    side_effect=("c", "l", "d", "c", "l", "s", "c", "s", "s", "c"),
                ):
                    with mock.patch(
                        "monopoly.models.interfaces.lists.input",
                        side_effect=("0000", land.id, "c", land.id, "c", stock.id, "c"),
                    ):
                        _value = player.cash + land.sale_value + stock.sale_value + player_land.sale_value

                        assert player.prepare_payment(board, _value, force=True) is True
                        assert player.cash == _value
                assert mock_input.call_count == 0
            assert mock_bankrupt.call_count == 0

    def test_failed_net_worth(
        self,
        board: Board,
        player: Player,
    ):
        with mock.patch("monopoly.models.equipments.players.Player.bankrupt") as mock_bankrupt:
            with mock.patch("monopoly.models.equipments.players.input") as mock_input:
                _cash = player.cash

                assert player.prepare_payment(board, (1 << 32) - 1) is False
                assert player.cash == _cash
                assert mock_input.call_count == 0
            assert mock_bankrupt.call_count == 0

    def test_failed_net_worth_force(
        self,
        board: Board,
        player: Player,
    ):
        with mock.patch("monopoly.models.equipments.players.Player.bankrupt") as mock_bankrupt:
            with mock.patch("monopoly.models.equipments.players.input") as mock_input:
                _cash = player.cash

                assert player.prepare_payment(board, (1 << 32) - 1, force=True) is True
                assert player.cash == _cash
                assert mock_input.call_count == 1
            assert mock_bankrupt.call_count == 1


class TestPlayerRepresentation:
    def test_success(
        self,
        player_land: PlayerLand,
        player_ocean: PlayerLand,
        player_stock: PlayerStock,
    ):
        for item in (
            player_land.player, player_land.land,
            player_ocean.player, player_ocean.land,
            player_stock.player, player_stock.stock,
        ):
            assert repr(item)
