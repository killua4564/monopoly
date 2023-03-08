from unittest import mock

import pytest

from monopoly.models.boards import Board
from monopoly.models.equipments.players import Player, PlayerStock
from monopoly.models.properties.stocks import ETF, Stock


class TestBuyingStock:
    def test_success(self, board: Board, player: Player, stock: Stock):
        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", stock.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "c")):
                _cash = player.cash
                _amount = stock.amount

                board.buy_stock(player)

                assert player.cash == _cash - stock.value
                assert stock.amount == _amount - 1
                assert player.stocks[stock.id].amount == 1

    def test_success_opening(self, board: Board, player: Player, stock: Stock):
        for _ in range(10):
            board.opening_stocks()

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", stock.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "c")):
                _cash = player.cash
                _amount = stock.amount

                board.buy_stock(player)

                assert player.cash == _cash - stock.value
                assert stock.amount == _amount - 1
                assert player.stocks[stock.id].amount == 1

    def test_success_twice(self, board: Board, player: Player, stock: Stock):
        player.cash = (1 << 32) - 1

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", stock.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "b", "c")):
                _cash = player.cash
                _amount = stock.amount

                board.buy_stock(player)

                assert player.cash == _cash - 2 * stock.value
                assert stock.amount == _amount - 2
                assert player.stocks[stock.id].amount == 2

    def test_failed_insufficient_cash(self, board: Board, player: Player, stock: Stock):
        player.cash = 1

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", stock.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "c")):
                _cash = player.cash
                _amount = stock.amount

                board.buy_stock(player)

                assert player.cash == _cash
                assert stock.amount == _amount
                with pytest.raises(KeyError):
                    assert player.stocks[stock.id]

    def test_failed_insufficient_amount(self, board: Board, player: Player, stock: Stock):
        stock.amount = 0

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", stock.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "c")):
                _cash = player.cash
                _amount = stock.amount

                board.buy_stock(player)

                assert player.cash == _cash
                assert stock.amount == _amount
                with pytest.raises(KeyError):
                    assert player.stocks[stock.id]


class TestBuyingEtf:
    def test_success(self, board: Board, player: Player, etf: ETF):
        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", etf.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "c")):
                _cash = player.cash
                _amount = etf.amount

                board.buy_stock(player)

                assert player.cash == _cash - etf.value
                assert etf.amount == _amount - 1
                assert player.stocks[etf.id].amount == 1

    def test_success_opening(self, board: Board, player: Player, etf: ETF):
        for _ in range(10):
            board.opening_stocks()

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", etf.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "c")):
                _cash = player.cash
                _amount = etf.amount

                board.buy_stock(player)

                assert player.cash == _cash - etf.value
                assert etf.amount == _amount - 1
                assert player.stocks[etf.id].amount == 1

    def test_success_twice(self, board: Board, player: Player, etf: ETF):
        player.cash = (1 << 32) - 1

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", etf.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "b", "c")):
                _cash = player.cash
                _amount = etf.amount

                board.buy_stock(player)

                assert player.cash == _cash - 2 * etf.value
                assert etf.amount == _amount - 2
                assert player.stocks[etf.id].amount == 2

    def test_failed_insufficient_cash(self, board: Board, player: Player, etf: ETF):
        player.cash = 1

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", etf.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "c")):
                _cash = player.cash
                _amount = etf.amount

                board.buy_stock(player)

                assert player.cash == _cash
                assert etf.amount == _amount
                with pytest.raises(KeyError):
                    assert player.stocks[etf.id]

    def test_failed_insufficient_amount(self, board: Board, player: Player, etf: ETF):
        etf.amount = 0

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", etf.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "b", "c")):
                _cash = player.cash
                _amount = etf.amount

                board.buy_stock(player)

                assert player.cash == _cash
                assert etf.amount == _amount
                with pytest.raises(KeyError):
                    assert player.stocks[etf.id]


class TestSellingStock:
    def test_success(self, board: Board, player_stock: PlayerStock):
        player, stock = player_stock.player, player_stock.stock

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", stock.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s", "c")):
                _cash = player.cash
                _amount = stock.amount

                player.trading_stocks_off(board)

                assert player.cash == _cash + stock.sale_value
                assert stock.amount == _amount + 1
                assert player.incoming == 0
                with pytest.raises(KeyError):
                    assert player.stocks[stock.id]

    def test_success_opening(self, board: Board, player_stock: PlayerStock):
        player, stock = player_stock.player, player_stock.stock
        for _ in range(10):
            board.opening_stocks()

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", stock.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s", "c")):
                _cash = player.cash
                _amount = stock.amount

                player.trading_stocks_off(board)

                assert player.cash == _cash + stock.sale_value
                assert stock.amount == _amount + 1
                assert player.incoming == 0
                with pytest.raises(KeyError):
                    assert player.stocks[stock.id]

    def test_success_twice(self, board: Board, player_stock: PlayerStock):
        player, stock = player_stock.player, player_stock.stock
        player_stock.amount = 2

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", stock.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s", "s", "c")):
                _cash = player.cash
                _amount = stock.amount

                player.trading_stocks_off(board)

                assert player.cash == _cash + 2 * stock.sale_value
                assert stock.amount == _amount + 2
                assert player.incoming == 0
                with pytest.raises(KeyError):
                    assert player.stocks[stock.id]

    def test_success_remaining(self, board: Board, player_stock: PlayerStock):
        player, stock = player_stock.player, player_stock.stock
        player_stock.amount = 2

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", stock.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s", "c")):
                _cash = player.cash
                _amount = stock.amount

                player.trading_stocks_off(board)

                assert player.cash == _cash + stock.sale_value
                assert stock.amount == _amount + 1
                assert player.incoming == 0
                assert player.stocks[stock.id].amount == 1

    def test_success_silent(self, board: Board, player_stock: PlayerStock):
        player, stock = player_stock.player, player_stock.stock

        with mock.patch("monopoly.models.properties.stocks.print") as mock_print:
            _cash = player.cash
            _amount = stock.amount

            stock.selling(player, board, silent=True)

            assert player.cash == _cash + stock.sale_value
            assert stock.amount == _amount + 1
            assert player.incoming == 0
            with pytest.raises(KeyError):
                assert player.stocks[stock.id]
            assert mock_print.call_count == 0

    def test_failed_insufficient_amount(self, board: Board, player_stock: PlayerStock):
        player, stock = player_stock.player, player_stock.stock
        player_stock.amount = 0

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", stock.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s", "c")):
                _cash = player.cash
                _amount = stock.amount

                player.trading_stocks_off(board)

                assert player.cash == _cash
                assert stock.amount == _amount
                assert player.incoming == 0
                assert player.stocks[stock.id].amount == 0


class TestSellingEtf:
    def test_success(self, board: Board, player_etf: PlayerStock):
        player, etf = player_etf.player, player_etf.stock

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", etf.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s", "c")):
                _cash = player.cash
                _amount = etf.amount

                player.trading_stocks_off(board)

                assert player.cash == _cash + etf.sale_value
                assert etf.amount == _amount + 1
                assert player.incoming == 0
                with pytest.raises(KeyError):
                    assert player.stocks[etf.id]

    def test_success_opening(self, board: Board, player_etf: PlayerStock):
        player, etf = player_etf.player, player_etf.stock
        for _ in range(10):
            board.opening_stocks()

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", etf.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s", "c")):
                _cash = player.cash
                _amount = etf.amount

                player.trading_stocks_off(board)

                assert player.cash == _cash + etf.sale_value
                assert etf.amount == _amount + 1
                assert player.incoming == 0
                with pytest.raises(KeyError):
                    assert player.stocks[etf.id]

    def test_success_twice(self, board: Board, player_etf: PlayerStock):
        player, etf = player_etf.player, player_etf.stock
        player_etf.amount = 2

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", etf.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s", "s", "c")):
                _cash = player.cash
                _amount = etf.amount

                player.trading_stocks_off(board)

                assert player.cash == _cash + 2 * etf.sale_value
                assert etf.amount == _amount + 2
                assert player.incoming == 0
                with pytest.raises(KeyError):
                    assert player.stocks[etf.id]

    def test_success_remaining(self, board: Board, player_etf: PlayerStock):
        player, etf = player_etf.player, player_etf.stock
        player_etf.amount = 2

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", etf.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s", "c")):
                _cash = player.cash
                _amount = etf.amount

                player.trading_stocks_off(board)

                assert player.cash == _cash + etf.sale_value
                assert etf.amount == _amount + 1
                assert player.incoming == 0
                assert player.stocks[etf.id].amount == 1

    def test_success_silent(self, board: Board, player_etf: PlayerStock):
        player, etf = player_etf.player, player_etf.stock

        with mock.patch("monopoly.models.properties.stocks.print") as mock_print:
            _cash = player.cash
            _amount = etf.amount

            etf.selling(player, board, silent=True)

            assert player.cash == _cash + etf.sale_value
            assert etf.amount == _amount + 1
            assert player.incoming == 0
            with pytest.raises(KeyError):
                assert player.stocks[etf.id]
            assert mock_print.call_count == 0

    def test_failed_insufficient_amount(self, board: Board, player_etf: PlayerStock):
        player, etf = player_etf.player, player_etf.stock
        player_etf.amount = 0

        with mock.patch("monopoly.models.interfaces.lists.input", side_effect=("0000", etf.id, "c")):
            with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("i", "m", "s", "c")):
                _cash = player.cash
                _amount = etf.amount

                player.trading_stocks_off(board)

                assert player.cash == _cash
                assert etf.amount == _amount
                assert player.incoming == 0
                assert player.stocks[etf.id].amount == 0
