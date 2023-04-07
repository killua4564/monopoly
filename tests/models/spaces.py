from unittest import mock

import pytest

from monopoly.constants import CardType
from monopoly.models.boards import Board, BoardPlayer
from monopoly.models.equipments import spaces as models
from monopoly.models.equipments.players import Player, PlayerLand


class TestCardSpace:
    @pytest.fixture(name="chance_space")
    def fixture_chance_space(
        self,
        spaces: dict[str, models.BaseSpace],
    ) -> models.CardSpace:
        return spaces["CHANCE01"]

    @pytest.fixture(name="community_chest_space")
    def fixture_community_chest_space(
        self,
        spaces: dict[str, models.BaseSpace],
    ) -> models.CardSpace:
        return spaces["COMMUNITY_CHEST01"]

    def test_success_arrive_chance(
        self,
        board: Board,
        player: Player,
        chance_space: models.CardSpace,
    ):
        mock_card = mock.Mock()
        board.cards[CardType.CHANCE] = [mock_card]

        with mock.patch("monopoly.models.equipments.spaces.input") as mock_input:
            chance_space.arrive(player, board=board)

            assert mock_input.call_count == 2
            assert mock_card.execute.call_count == 1
            assert mock_card.execute.call_args == mock.call(player, board=board)

    def test_success_arrive_community_chest(
        self,
        board: Board,
        player: Player,
        community_chest_space: models.CardSpace,
    ):
        mock_card = mock.Mock()
        board.cards[CardType.COMMUNITY_CHEST] = [mock_card]

        with mock.patch("monopoly.models.equipments.spaces.input") as mock_input:
            community_chest_space.arrive(player, board=board)

            assert mock_input.call_count == 2
            assert mock_card.execute.call_count == 1
            assert mock_card.execute.call_args == mock.call(player, board=board)


class TestCashSpace:
    @pytest.fixture(name="earning_space")
    def fixture_earning_space(
        self,
        spaces: dict[str, models.BaseSpace],
    ) -> models.CashSpace:
        return spaces["EARNING01"]

    @pytest.fixture(name="costing_space")
    def fixture_costing_space(
        self,
        spaces: dict[str, models.BaseSpace],
    ) -> models.CashSpace:
        return spaces["COSTING01"]

    def test_success_arrive_earning(
        self,
        board: Board,
        player: Player,
        earning_space: models.CashSpace,
    ):
        with mock.patch("monopoly.models.equipments.spaces.input") as mock_input:
            _cash = player.cash

            earning_space.arrive(player, board=board)

            assert player.cash == _cash + earning_space.value
            assert player.incoming == earning_space.value
            assert mock_input.call_count == 1

    def test_success_arrive_costing(
        self,
        board: Board,
        player: Player,
        costing_space: models.CashSpace,
    ):
        with mock.patch("monopoly.models.equipments.spaces.input") as mock_input:
            _cash = player.cash

            costing_space.arrive(player, board=board)

            assert player.cash == _cash - costing_space.value
            assert mock_input.call_count == 1

    def test_failed_arrive_costing_bankruptcy(
        self,
        board: Board,
        player: Player,
        costing_space: models.CashSpace,
    ):
        costing_space.value = (1 << 32) - 1
        with mock.patch("monopoly.models.equipments.spaces.input") as mock_space_input:
            with mock.patch("monopoly.models.equipments.players.input") as mock_player_input:
                _cash = player.cash

                costing_space.arrive(player, board=board)

                assert player.bankruptcy is True
                assert player.cash == _cash - costing_space.value
                assert mock_space_input.call_count == 1
                assert mock_player_input.call_count == 1


class TestLandSpace:
    @pytest.fixture(name="land_space")
    def fixture_land_space(
        self,
        spaces: dict[str, models.BaseSpace],
    ) -> models.LandSpace:
        return spaces["1001"]

    @pytest.fixture(name="ocean_space")
    def fixture_ocean_space(
        self,
        spaces: dict[str, models.BaseSpace],
    ) -> models.LandSpace:
        return spaces["9001"]

    def test_success_arrive_buying(
        self,
        board: Board,
        player: Player,
        land_space: models.LandSpace,
    ):
        land = land_space.land

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("b", "c")):
            with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=True):
                _cash = player.cash

                land_space.arrive(player, board=board)

                assert land.has_owner is True
                assert player.cash == _cash - land.land_price
                assert land.stock.earning == int(land.land_price * land.stock.payout_ratio)
                assert player.lands[land.id].houses == 0
                assert board.credentials[land.id].houses == 0

    def test_success_arrive_tolling(
        self,
        board: Board,
        player_land: PlayerLand,
        land_space: models.LandSpace,
        new_board_player: BoardPlayer,
    ):
        player, land = player_land.player, player_land.land
        board.current_player, new_player = new_board_player, new_board_player.player

        with mock.patch("monopoly.models.equipments.players.input") as mock_input:
            _cash = player.cash
            _new_cash = new_player.cash
            _value = player_land.tolling_value

            land_space.arrive(new_player, board=board)

            assert player.cash == _cash + _value
            assert player.incoming == _value
            assert new_player.cash == _new_cash - _value
            assert land.stock.earning == int(_value * land.stock.payout_ratio)
            assert mock_input.call_count == 1

    def test_success_arrive_tolling_ocean(
        self,
        board: Board,
        player_ocean: PlayerLand,
        ocean_space: models.LandSpace,
        new_board_player: BoardPlayer,
    ):
        player = player_ocean.player
        board.current_player, new_player = new_board_player, new_board_player.player

        with mock.patch("monopoly.models.equipments.players.input") as mock_input:
            _cash = player.cash
            _new_cash = new_player.cash
            _value = player_ocean.tolling_value

            ocean_space.arrive(new_player, board=board)

            assert player.cash == _cash + _value
            assert player.incoming == _value
            assert new_player.cash == _new_cash - _value
            assert mock_input.call_count == 1

    def test_success_arrive_tolling_advanced(
        self,
        board: Board,
        player_land: PlayerLand,
        land_space: models.LandSpace,
        new_board_player: BoardPlayer,
    ):
        player, land = player_land.player, player_land.land
        board.current_player, new_player = new_board_player, new_board_player.player
        player_land.houses = 1
        player.get_or_create_player_land(board.lands["1002"])

        with mock.patch("monopoly.models.equipments.players.input") as mock_input:
            _cash = player.cash
            _new_cash = new_player.cash
            _value = player_land.tolling_value

            land_space.arrive(new_player, board=board)

            assert player.cash == _cash + _value
            assert player.incoming == _value
            assert new_player.cash == _new_cash - _value
            assert land.stock.earning == int(_value * land.stock.payout_ratio)
            assert _value > land.tolls[1]
            assert mock_input.call_count == 1

    def test_success_arrive_free_tolling(
        self,
        board: Board,
        player_land: PlayerLand,
        land_space: models.LandSpace,
        new_board_player: BoardPlayer,
    ):
        player, land = player_land.player, player_land.land
        board.current_player, new_player = new_board_player, new_board_player.player
        new_board_player.can_free_tolling = True

        with mock.patch("monopoly.models.equipments.players.input") as mock_input:
            _cash = player.cash
            _new_cash = new_player.cash

            land_space.arrive(new_player, board=board)

            assert player.cash == _cash
            assert player.incoming == 0
            assert new_player.cash == _new_cash
            assert land.stock.earning == 0
            assert mock_input.call_count == 1

    def test_success_arrive_construction(
        self,
        board: Board,
        player_land: PlayerLand,
        land_space: models.LandSpace,
    ):
        player, land = player_land.player, player_land.land

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("b", "c")):
            with mock.patch("monopoly.models.equipments.players.configs.BUILDING_UPPERBOUND", new=4):
                with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=True):
                    _cash = player.cash
                    _houses = player_land.houses

                    land_space.arrive(player, board=board)

                    assert player_land.houses == _houses + 1
                    assert player.cash == _cash - land.house_price
                    assert land.stock.earning == int(land.house_price * land.stock.payout_ratio)

    def test_success_arrive_construction_unbuildable(
        self,
        board: Board,
        player_ocean: PlayerLand,
        ocean_space: models.LandSpace,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("b", "c")):
            with mock.patch("monopoly.models.equipments.players.configs.BUILDING_UPPERBOUND", new=4):
                with mock.patch("monopoly.models.equipments.players.configs.UNLIMITED_BUILDING", new=True):
                    _cash = player_ocean.player.cash
                    _houses = player_ocean.houses

                    ocean_space.arrive(player_ocean.player, board=board)

                    assert player_ocean.houses == _houses
                    assert player_ocean.player.cash == _cash


class TestPausePlayerSpace:
    @pytest.fixture(name="pause_space")
    def fixture_pause_space(
        self,
        spaces: dict[str, models.BaseSpace],
    ) -> models.PausePlayerSpace:
        return spaces["PAUSEPLAYER"]

    def test_success_arrive(
        self,
        board: Board,
        board_player: BoardPlayer,
        pause_space: models.PausePlayerSpace,
    ):
        with mock.patch("monopoly.models.equipments.spaces.input") as mock_input:
            _unmovable = board_player.unmovable

            pause_space.arrive(board_player.player, board=board)

            assert board_player.unmovable == _unmovable + pause_space.value
            assert mock_input.call_count == 1


class TestStartPointSpace:
    @pytest.fixture(name="start_point_space")
    def fixture_start_point_space(
        self,
        spaces: dict[str, models.BaseSpace],
    ) -> models.StartPointSpace:
        return spaces["STARTPOINT"]

    def test_success_arrive(
        self,
        board: Board,
        player: Player,
        start_point_space: models.StartPointSpace,
    ):
        with mock.patch("monopoly.models.equipments.spaces.input", return_value="n") as mock_input:
            _direction = board.direction

            start_point_space.arrive(player, board=board)

            assert board.direction == _direction
            assert mock_input.call_count == 1

    def test_success_arrive_reversing(
        self,
        board: Board,
        player: Player,
        start_point_space: models.StartPointSpace,
    ):
        with mock.patch("monopoly.models.equipments.spaces.input", return_value="y") as mock_input:
            _direction = board.direction

            start_point_space.arrive(player, board=board)

            assert board.direction != _direction
            assert mock_input.call_count == 2

    def test_success_pass_by(
        self,
        board: Board,
        player: Player,
        start_point_space: models.StartPointSpace,
    ):
        with mock.patch("monopoly.models.interfaces.lists.input", return_value="c") as mock_input:
            _cash = player.cash

            start_point_space.pass_by(player, board=board)

            assert player.cash == _cash + start_point_space.value
            assert player.incoming == start_point_space.value
            assert mock_input.call_count == 1


class TestThreeDicesSpace:
    @pytest.fixture(name="three_dices_space")
    def fixture_three_dices_space(
        self,
        spaces: dict[str, models.BaseSpace],
    ) -> models.ThreeDicesSpace:
        return spaces["THREEDICES"]

    def test_success_arrive(
        self,
        board: Board,
        board_player: BoardPlayer,
        three_dices_space: models.ThreeDicesSpace,
    ):
        with mock.patch("monopoly.models.equipments.spaces.input") as mock_input:
            three_dices_space.arrive(board_player.player, board=board)

            assert board_player.can_three_dices is True
            assert mock_input.call_count == 1


class TestTransportStartPointSpace:
    @pytest.fixture(name="start_point_space")
    def fixture_start_point_space(
        self,
        spaces: dict[str, models.BaseSpace],
    ) -> models.StartPointSpace:
        return spaces["STARTPOINT"]

    @pytest.fixture(name="trans_start_point_space")
    def fixture_trans_start_point_space(
        self,
        spaces: dict[str, models.BaseSpace],
    ) -> models.TransportStartPointSpace:
        return spaces["TRANSTARTPOINT"]

    def test_success_arrive(
        self,
        board: Board,
        board_player: BoardPlayer,
        trans_start_point_space: models.TransportStartPointSpace,
    ):
        with mock.patch("monopoly.models.equipments.spaces.input", return_value="n"):
            _space = board_player.space

            trans_start_point_space.arrive(board_player.player, board=board)

            assert board_player.space == _space

    def test_success_arrive_transporting(
        self,
        board: Board,
        board_player: BoardPlayer,
        start_point_space: models.StartPointSpace,
        trans_start_point_space: models.TransportStartPointSpace,
    ):
        with mock.patch("monopoly.models.equipments.spaces.input", return_value="y"):
            with mock.patch("monopoly.models.equipments.spaces.StartPointSpace.arrive") as mock_arrive:
                with mock.patch("monopoly.models.equipments.spaces.StartPointSpace.pass_by") as mock_pass_by:
                    trans_start_point_space.arrive(board_player.player, board=board)

                    assert board_player.space.space == start_point_space
                    assert mock_arrive.call_count == 1
                    assert mock_pass_by.call_count == 1
