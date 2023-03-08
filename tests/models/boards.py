from unittest import mock

from monopoly.constants import DirectionAttr
from monopoly.models.boards import Board, BoardPlayer, BoardSpace


class TestBoardLoad:
    def test_success(
        self,
        board: Board,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", return_value="_test_file"):
            with mock.patch("monopoly.models.boards.pathlib.PosixPath.read_bytes") as mock_read:
                with mock.patch("monopoly.models.boards.pickle.loads") as mock_loads:
                    board.load()

                    assert mock_loads.call_count == 1
                assert mock_read.call_count == 1

    def test_success_saved_files(
        self,
        board: Board,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", return_value="_test_file.sav"):
            with mock.patch("monopoly.models.boards.pathlib.PosixPath.read_bytes") as mock_read:
                with mock.patch("monopoly.models.boards.pickle.loads") as mock_loads:
                    with mock.patch("monopoly.models.boards.Board._get_saved_files", return_value=[
                        mock.Mock(name=f"_test_file_{idx}.sav") for idx in range(10)
                    ]):
                        board.load()

                    assert mock_loads.call_count == 1
                assert mock_read.call_count == 1

    def test_success_loading(
        self,
        board: Board,
    ):
        filename: str = "_test_file"

        with mock.patch("monopoly.models.interfaces.menus.input", return_value=filename):
            with mock.patch("monopoly.models.boards.pathlib.PosixPath.read_bytes") as mock_read:
                with mock.patch("monopoly.models.boards.pickle.loads") as mock_loads:
                    with mock.patch("monopoly.models.boards.Board.loading") as mock_loading:
                        board.load()

                        assert mock_loading.call_args.args[0].name == f"{filename}.sav"
                    assert mock_loads.call_count == 0
                assert mock_read.call_count == 0

    def test_failed_filename(
        self,
        board: Board,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", return_value="../_test_file.sav"):
            with mock.patch("monopoly.models.boards.pathlib.PosixPath.read_bytes") as mock_read:
                with mock.patch("monopoly.models.boards.pickle.loads") as mock_loads:
                    assert board.load() is None
                    assert mock_loads.call_count == 0
                assert mock_read.call_count == 0

    def test_failed_pickle(
        self,
        board: Board,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", return_value="_test_file"):
            with mock.patch("monopoly.models.boards.pathlib.PosixPath.read_bytes") as mock_read:
                with mock.patch("monopoly.models.boards.pickle.loads", side_effect=EOFError):
                    assert board.load() is None
                assert mock_read.call_count == 1


class TestBoardRepresentation:
    def test_success(
        self,
        board_player: BoardPlayer,
    ):
        for item in (
            board_player.board, board_player.player,
            board_player.board.start_space.space,
        ):
            assert repr(item)


class TestBoardReverseDirection:
    def test_success_forwards(
        self,
        board: Board,
    ):
        board.direction = DirectionAttr.FORWARDS
        board.reverse_direction()
        assert board.direction == DirectionAttr.BACKWARDS

    def test_success_backwards(
        self,
        board: Board,
    ):
        board.direction = DirectionAttr.BACKWARDS
        board.reverse_direction()
        assert board.direction == DirectionAttr.FORWARDS


class TestBoardRun:
    def test_success_forwards(
        self,
        board: Board,
    ):
        with mock.patch("monopoly.models.boards.BoardPlayer.play") as mock_play:
            with mock.patch("monopoly.models.boards.Board.opening_stocks") as mock_opening:
                _current_player = board.current_player

                board.run()

                assert board.finished is False
                assert board.current_player == _current_player.get_forwards()
                assert board.direction == DirectionAttr.FORWARDS
                assert mock_opening.call_count == 0
            assert mock_play.call_count == 1

    def test_success_backwards(
        self,
        board: Board,
    ):
        board.reverse_direction()
        with mock.patch("monopoly.models.boards.BoardPlayer.play") as mock_play:
            with mock.patch("monopoly.models.boards.Board.opening_stocks") as mock_opening:
                _current_player = board.current_player

                board.run()

                assert board.finished is False
                assert board.current_player == _current_player.get_backwards()
                assert board.direction == DirectionAttr.BACKWARDS
                assert mock_opening.call_count == 0
            assert mock_play.call_count == 1

    def test_success_opening(
        self,
        board: Board,
    ):
        board.current_player = board.current_player.get_backwards()

        with mock.patch("monopoly.models.boards.BoardPlayer.play") as mock_play:
            with mock.patch("monopoly.models.boards.Board.opening_stocks") as mock_opening:

                board.run()

                assert board.finished is False
                assert mock_opening.call_count == 1
            assert mock_play.call_count == 1

    def test_success_winner(
        self,
        board: Board,
    ):
        board.current_player.player.surrender = True

        with mock.patch("monopoly.models.boards.BoardPlayer.play") as mock_play:
            with mock.patch("monopoly.models.boards.Board.opening_stocks") as mock_opening:

                board.run()

                assert board.finished is True
                assert mock_opening.call_count == 0
            assert mock_play.call_count == 0


class TestBoardSave:
    def test_success(
        self,
        board: Board,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", return_value="_test_file"):
            with mock.patch("monopoly.models.boards.pathlib.PosixPath.write_bytes") as mock_write:
                board.save()

                assert mock_write.call_count == 1

    def test_success_saved_files(
        self,
        board: Board,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", return_value="_test_file.sav"):
            with mock.patch("monopoly.models.boards.pathlib.PosixPath.write_bytes") as mock_write:
                with mock.patch("monopoly.models.boards.Board._get_saved_files", return_value=[
                    mock.Mock(name=f"_test_file_{idx}.sav") for idx in range(10)
                ]):
                    board.save()

                    assert mock_write.call_count == 1

    def test_success_saving(
        self,
        board: Board,
    ):
        filename: str = "_test_file"

        with mock.patch("monopoly.models.interfaces.menus.input", return_value=filename):
            with mock.patch("monopoly.models.boards.pathlib.PosixPath.write_bytes") as mock_write:
                with mock.patch("monopoly.models.boards.Board.saving") as mock_saving:
                    board.save()

                    assert mock_saving.call_args.args[0].name == f"{filename}.sav"
                assert mock_write.call_count == 0

    def test_failed_filename(
        self,
        board: Board,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", return_value="../_test_file.sav"):
            with mock.patch("monopoly.models.boards.pathlib.PosixPath.write_bytes") as mock_write:
                board.save()

                assert mock_write.call_count == 0


class TestBoardStart:
    def test_success(
        self,
        unstarted_board: Board,
    ):
        assert unstarted_board.current_player is None
        assert unstarted_board.players == []

        unstarted_board.start()

        assert unstarted_board.current_player == unstarted_board.start_player
        assert unstarted_board.players == [
            player.player for player in unstarted_board.board_players
        ]
        assert all(
            player.space == unstarted_board.start_space
            for player in unstarted_board.board_players
        )


class TestBoardTheMostPlayer:
    def test_success(
        self,
        board_player: BoardPlayer,
        new_board_player: BoardPlayer,
    ):
        board = board_player.board
        board_player.unmovable = 1
        new_board_player.unmovable = 2

        assert board.get_the_most_player(
            lambda x, y: x.unmovable > y.unmovable,
        ) == board_player
        assert board.get_the_most_player(
            lambda x, y: x.unmovable < y.unmovable,
        ) == new_board_player

    def test_success_poorest_richest_player(
        self,
        board_player: BoardPlayer,
        new_board_player: BoardPlayer,
    ):
        board = board_player.board
        board_player.player.cash = 1
        new_board_player.player.cash = 2

        assert board.poorest_player == board_player.player
        assert board.richest_player == new_board_player.player


class TestBoardPlayerPlay:
    def test_success_two_dices(
        self,
        board_player: BoardPlayer,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("l", "s", "p", "t", "d")):
            with mock.patch("monopoly.models.equipments.players.Player.trade_off") as mock_trade_off:
                with mock.patch("monopoly.models.boards.input", side_effect=("2",)):
                    with mock.patch("monopoly.models.boards.BoardPlayer.moving") as mock_moving:
                        board_player.play()

                        assert mock_moving.call_count == 1
                        assert 2 <= mock_moving.call_args.args[0] <= 12
                assert mock_trade_off.call_count == 1

    def test_success_one_dices(
        self,
        board_player: BoardPlayer,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("l", "s", "p", "t", "d")):
            with mock.patch("monopoly.models.equipments.players.Player.trade_off") as mock_trade_off:
                with mock.patch("monopoly.models.boards.input", side_effect=("1",)):
                    with mock.patch("monopoly.models.boards.BoardPlayer.moving") as mock_moving:
                        board_player.play()

                        assert mock_moving.call_count == 1
                        assert 1 <= mock_moving.call_args.args[0] <= 6
                assert mock_trade_off.call_count == 1

    def test_success_three_dices(
        self,
        board_player: BoardPlayer,
    ):
        board_player.can_three_dices = True

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("l", "s", "p", "t", "d")):
            with mock.patch("monopoly.models.equipments.players.Player.trade_off") as mock_trade_off:
                with mock.patch("monopoly.models.boards.input", side_effect=("3",)):
                    with mock.patch("monopoly.models.boards.BoardPlayer.moving") as mock_moving:
                        board_player.play()

                        assert mock_moving.call_count == 1
                        assert 3 <= mock_moving.call_args.args[0] <= 18
                assert mock_trade_off.call_count == 1

    def test_success_two_dices_value_error(
        self,
        board_player: BoardPlayer,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("l", "s", "p", "t", "d")):
            with mock.patch("monopoly.models.equipments.players.Player.trade_off") as mock_trade_off:
                with mock.patch("monopoly.models.boards.input", side_effect=ValueError):
                    with mock.patch("monopoly.models.boards.BoardPlayer.moving") as mock_moving:
                        board_player.play()

                        assert mock_moving.call_count == 1
                        assert 2 <= mock_moving.call_args.args[0] <= 12
                assert mock_trade_off.call_count == 1

    def test_success_surrender(
        self,
        board_player: BoardPlayer,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("l", "s", "p", "t", "c", "n", "c", "y")):
            with mock.patch("monopoly.models.equipments.players.Player.trade_off") as mock_trade_off:
                with mock.patch("monopoly.models.boards.input", side_effect=ValueError):
                    with mock.patch("monopoly.models.boards.BoardPlayer.moving") as mock_moving:
                        board_player.play()

                        assert board_player.player.surrender is True
                        assert mock_moving.call_count == 0
                assert mock_trade_off.call_count == 1

    def test_success_save_game(
        self,
        board_player: BoardPlayer,
    ):
        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("l", "s", "p", "t", "save", "d")):
            with mock.patch("monopoly.models.equipments.players.Player.trade_off") as mock_trade_off:
                with mock.patch("monopoly.models.boards.input", side_effect=("2",)):
                    with mock.patch("monopoly.models.boards.BoardPlayer.moving") as mock_moving:
                        with mock.patch("monopoly.models.boards.Board.save") as mock_save:
                            board_player.play()

                            assert mock_save.call_count == 1
                        assert mock_moving.call_count == 1
                        assert 2 <= mock_moving.call_args.args[0] <= 12
                assert mock_trade_off.call_count == 1

    def test_failed_unmovable(
        self,
        board_player: BoardPlayer,
    ):
        board_player.unmovable = 1

        with mock.patch("monopoly.models.interfaces.menus.input", side_effect=("l", "s", "p", "t", "d")):
            with mock.patch("monopoly.models.equipments.players.Player.trade_off") as mock_trade_off:
                with mock.patch("monopoly.models.boards.input", side_effect=("2",)):
                    with mock.patch("monopoly.models.boards.BoardPlayer.moving") as mock_moving:
                        board_player.play()

                        assert mock_moving.call_count == 0
                assert mock_trade_off.call_count == 0


class TestBoardPlayerMoving:
    def _get_continuous_space(
        self,
        current_space: BoardSpace,
        *,
        direction: DirectionAttr = DirectionAttr.FORWARDS,
        k: int = 1,
    ) -> tuple[BoardSpace, BoardSpace, int]:
        while True:
            moving_points, next_space = 0, current_space
            for _ in range(k):
                next_space = getattr(next_space, direction.value)()
                moving_points += next_space.space.moving_point
                if isinstance(next_space, list):
                    break
            else:
                return (current_space, next_space, moving_points)
            current_space = getattr(current_space, direction.value)()

    def _get_discontinuous_space(
        self,
        current_space: BoardSpace,
        *,
        direction: DirectionAttr = DirectionAttr.FORWARDS,
    ) -> tuple[BoardSpace, list[BoardSpace]]:
        while True:
            next_space = current_space
            next_space = getattr(next_space, direction.value)()
            if isinstance(next_space, list):
                return (current_space, next_space)
            current_space = next_space

    def test_success_forwards_one_space(
        self,
        board_player: BoardPlayer,
    ):
        start_space, final_space, moving_points = self._get_continuous_space(board_player.space)

        with mock.patch("monopoly.models.boards.BoardPlayer.arrive") as mock_arrive:
            with mock.patch("monopoly.models.boards.BoardPlayer.pass_by") as mock_pass_by:
                board_player.space = start_space
                board_player.moving(moving_points)

                assert board_player.space == final_space
                assert mock_pass_by.call_count == 1
            assert mock_arrive.call_count == 1

    def test_success_forwards_two_space(
        self,
        board_player: BoardPlayer,
    ):
        start_space, final_space, moving_points = self._get_continuous_space(board_player.space, k=2)

        with mock.patch("monopoly.models.boards.BoardPlayer.arrive") as mock_arrive:
            with mock.patch("monopoly.models.boards.BoardPlayer.pass_by") as mock_pass_by:
                board_player.space = start_space
                board_player.moving(moving_points)

                assert board_player.space == final_space
                assert mock_pass_by.call_count == 2
            assert mock_arrive.call_count == 1

    def test_success_backwards_two_space(
        self,
        board_player: BoardPlayer,
    ):
        board_player.board.reverse_direction()
        start_space, final_space, moving_points = self._get_continuous_space(
            board_player.space,
            direction=board_player.board.direction,
            k=2,
        )

        with mock.patch("monopoly.models.boards.BoardPlayer.arrive") as mock_arrive:
            with mock.patch("monopoly.models.boards.BoardPlayer.pass_by") as mock_pass_by:
                board_player.space = start_space
                board_player.moving(moving_points)

                assert board_player.space == final_space
                assert mock_pass_by.call_count == 2
            assert mock_arrive.call_count == 1

    def test_success_forwards_branched_space(
        self,
        board_player: BoardPlayer,
    ):
        start_space, final_space = self._get_discontinuous_space(board_player.space)
        moving_index = 0

        with mock.patch("monopoly.models.boards.BoardPlayer.arrive") as mock_arrive:
            with mock.patch("monopoly.models.boards.BoardPlayer.pass_by") as mock_pass_by:
                with mock.patch("monopoly.models.boards.input", side_effect=(moving_index,)):
                    board_player.space = start_space
                    board_player.moving(final_space[moving_index].space.moving_point)

                    assert board_player.space == final_space[moving_index]
                assert mock_pass_by.call_count == 1
            assert mock_arrive.call_count == 1

    def test_success_forwards_branched_space_final_choice(
        self,
        board_player: BoardPlayer,
    ):
        start_space, final_space = self._get_discontinuous_space(board_player.space)
        moving_index = len(final_space) - 1

        with mock.patch("monopoly.models.boards.BoardPlayer.arrive") as mock_arrive:
            with mock.patch("monopoly.models.boards.BoardPlayer.pass_by") as mock_pass_by:
                with mock.patch("monopoly.models.boards.input", side_effect=(moving_index,)):
                    board_player.space = start_space
                    board_player.moving(final_space[moving_index].space.moving_point)

                    assert board_player.space == final_space[moving_index]
                assert mock_pass_by.call_count == 1
            assert mock_arrive.call_count == 1

    def test_success_forwards_branched_space_value_error(
        self,
        board_player: BoardPlayer,
    ):
        start_space, final_space = self._get_discontinuous_space(board_player.space)

        with mock.patch("monopoly.models.boards.BoardPlayer.arrive") as mock_arrive:
            with mock.patch("monopoly.models.boards.BoardPlayer.pass_by") as mock_pass_by:
                with mock.patch("monopoly.models.boards.input", side_effect=ValueError):
                    board_player.space = start_space
                    board_player.moving(final_space[0].space.moving_point)

                    assert board_player.space == final_space[0]
                assert mock_pass_by.call_count == 1
            assert mock_arrive.call_count == 1

    def test_success_backwards_branched_space(
        self,
        board_player: BoardPlayer,
    ):
        board_player.board.reverse_direction()
        start_space, final_space = self._get_discontinuous_space(
            board_player.space,
            direction=board_player.board.direction,
        )
        moving_index = 0

        with mock.patch("monopoly.models.boards.BoardPlayer.arrive") as mock_arrive:
            with mock.patch("monopoly.models.boards.BoardPlayer.pass_by") as mock_pass_by:
                with mock.patch("monopoly.models.boards.input", side_effect=(moving_index,)):
                    board_player.space = start_space
                    board_player.moving(final_space[moving_index].space.moving_point)

                    assert board_player.space == final_space[moving_index]
                assert mock_pass_by.call_count == 1
            assert mock_arrive.call_count == 1
