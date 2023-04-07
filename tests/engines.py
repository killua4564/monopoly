from unittest import mock

import pytest

from monopoly.engines import BaseEngine, StandAloneEngine


class TestEngineExecutionLoad:
    def test_success(
        self,
        engine: BaseEngine,
    ):
        mock_board = mock.Mock(auto_saving=mock.Mock())
        with mock.patch("monopoly.models.boards.Board.load", return_value=mock_board):
            with mock.patch("monopoly.engines.configs.DEBUG_MODE", new=False):
                with mock.patch("monopoly.engines.sys.exit") as mock_exit:
                    engine.execution_load()

                    assert engine.board == mock_board
                    assert mock_board.auto_saving.call_count == 0
                    assert mock_exit.call_count == 0

    def test_failed_value_error(
        self,
        engine: BaseEngine,
    ):
        with mock.patch("monopoly.models.boards.Board.load", side_effect=ValueError):
            with mock.patch("monopoly.engines.configs.DEBUG_MODE", new=False):
                with mock.patch("monopoly.engines.sys.exit") as mock_exit:
                    engine.execution_load()

                    assert mock_exit.call_count == 1

    def test_failed_value_error_debug(
        self,
        engine: BaseEngine,
    ):
        with mock.patch("monopoly.models.boards.Board.load", side_effect=ValueError):
            with mock.patch("monopoly.engines.configs.DEBUG_MODE", new=True):
                with mock.patch("monopoly.engines.sys.exit") as mock_exit:
                    with pytest.raises(ValueError):
                        engine.execution_load()

                    assert mock_exit.call_count == 0


class TestEngineExecutionNew:
    def test_success(
        self,
        engine: BaseEngine,
    ):
        mock_board = mock.Mock()
        with mock.patch("monopoly.loaders.fixture.FixtureLoader.execute", return_value=mock_board):
            with mock.patch("monopoly.engines.configs.DEBUG_MODE", new=False):
                with mock.patch("monopoly.engines.sys.exit") as mock_exit:
                    engine.execution_new()

                    assert engine.board == mock_board
                    assert mock_board.start.call_count == 1
                    assert mock_exit.call_count == 0

    def test_failed_value_error(
        self,
        engine: BaseEngine,
    ):
        with mock.patch("monopoly.loaders.fixture.FixtureLoader.execute", side_effect=ValueError):
            with mock.patch("monopoly.engines.configs.DEBUG_MODE", new=False):
                with mock.patch("monopoly.engines.sys.exit") as mock_exit:
                    engine.execution_new()

                    assert mock_exit.call_count == 1

    def test_failed_value_error_debug(
        self,
        engine: BaseEngine,
    ):
        with mock.patch("monopoly.loaders.fixture.FixtureLoader.execute", side_effect=ValueError):
            with mock.patch("monopoly.engines.configs.DEBUG_MODE", new=True):
                with mock.patch("monopoly.engines.sys.exit") as mock_exit:
                    with pytest.raises(ValueError):
                        engine.execution_new()

                    assert mock_exit.call_count == 0


class TestEngineExecutionStaff:
    def test_success(
        self,
        engine: BaseEngine,
    ):
        with mock.patch("monopoly.engines.print") as mock_print:
            engine.execution_staff()

            assert mock_print.call_count == 1


class TestStandAloneEngineExecute:
    def test_success_menu(
        self,
        stand_alone_engine: StandAloneEngine,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("n", "l", "s", "c")):
            with mock.patch.multiple(
                "monopoly.engines.StandAloneEngine",
                execution_new=mock.Mock(return_value=mock.Mock()),
                execution_load=mock.Mock(return_value=mock.Mock()),
                execution_staff=mock.Mock(return_value=mock.Mock()),
            ):
                stand_alone_engine.execute()
                assert stand_alone_engine.board is None

    def test_success_board(
        self,
        stand_alone_engine: StandAloneEngine,
    ):
        stand_alone_engine.board = mock.Mock()
        type(stand_alone_engine.board).finished = mock.PropertyMock(side_effect=(False, True))

        stand_alone_engine.execute()

        assert stand_alone_engine.board.run.call_count == 1

    def test_failed_value_error(
        self,
        stand_alone_engine: StandAloneEngine,
    ):
        stand_alone_engine.board = mock.Mock(
            finished=False,
            run=mock.Mock(side_effect=ValueError),
        )

        with mock.patch("monopoly.engines.configs.DEBUG_MODE", new=False):
            with mock.patch("monopoly.engines.sys.exit") as mock_exit:
                stand_alone_engine.execute()

                assert mock_exit.call_count == 1

    def test_failed_value_error_debug(
        self,
        stand_alone_engine: StandAloneEngine,
    ):
        stand_alone_engine.board = mock.Mock(
            finished=False,
            run=mock.Mock(side_effect=ValueError),
        )

        with mock.patch("monopoly.engines.configs.DEBUG_MODE", new=True):
            with mock.patch("monopoly.engines.sys.exit") as mock_exit:
                with pytest.raises(ValueError):
                    stand_alone_engine.execute()

                assert mock_exit.call_count == 0
