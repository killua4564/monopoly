import collections
import contextlib
import itertools
import typing
from unittest import mock

import pytest

from monopoly.constants import CashType
from monopoly.loaders import FixtureLoader
from monopoly.models.boards import Board, BoardPlayer
from monopoly.models.equipments import BaseCard, BaseSpace
from monopoly.models.equipments.players import Player, PlayerLand, PlayerStock
from monopoly.models.properties import ETF, Land, Ocean, Stock


@pytest.fixture(name="unstarted_board")
def fixture_unstarted_board() -> Board:
    with mock.patch(
        "monopoly.loaders.fixture.input",
        side_effect=("2", "_test_validate_error_username", "_test1", "_test2"),
    ):
        return FixtureLoader().execute()


@pytest.fixture(name="board")
def fixture_board(unstarted_board: Board) -> Board:
    unstarted_board.start()
    return unstarted_board


@pytest.fixture(name="board_player")
def fixture_board_player(board: Board) -> BoardPlayer:
    return board.current_player


@pytest.fixture(name="player")
def fixture_player(board_player: BoardPlayer) -> Player:
    return board_player.player


@pytest.fixture(name="new_board_player")
def fixture_new_board_player(board: Board) -> BoardPlayer:
    return getattr(board.current_player, board.direction.value)()


@pytest.fixture(name="new_player")
def fixture_new_player(new_board_player: BoardPlayer) -> Player:
    return new_board_player.player


@pytest.fixture(name="cards")
def fixture_cards(board: Board) -> dict[
    tuple[str, typing.Union[CashType, None]],
    BaseCard,
]:
    return {
        (card.__class__.__name__, getattr(card, "cash_type", None)): card
        for card in itertools.chain.from_iterable(board.cards.values())
    }


@pytest.fixture(name="spaces")
def fixture_spaces(board: Board) -> dict[str, BaseSpace]:
    queue = collections.deque()
    result: dict[str, BaseSpace] = {}

    queue.append(board.start_space)
    while queue:
        space = queue.popleft()
        with contextlib.suppress(KeyError):
            _ = result[space.space.id]
            continue

        result[space.space.id] = space.space
        next_space = getattr(space, board.direction.value)()
        if isinstance(next_space, list):
            queue.extend(next_space)
        else:
            queue.append(next_space)

    return result


@pytest.fixture(name="land")
def fixture_land(board: Board) -> Land:
    return board.lands["1001"]


@pytest.fixture(name="ocean")
def fixture_ocean(board: Board) -> Ocean:
    return board.lands["9001"]


@pytest.fixture(name="stock")
def fixture_stock(board: Board) -> Stock:
    return board.stocks["1001"]


@pytest.fixture(name="etf")
def fixture_etf(board: Board) -> ETF:
    return board.stocks["0011"]


@pytest.fixture(name="player_land")
def fixture_player_land(board: Board, player: Player, land: Land) -> PlayerLand:
    land.has_owner = True
    credential = player.get_or_create_player_land(land)
    return board.get_or_create_credential(land, credential=credential)


@pytest.fixture(name="player_ocean")
def fixture_player_ocean(board: Board, player: Player, ocean: Ocean) -> PlayerLand:
    ocean.has_owner = True
    credential = player.get_or_create_player_land(ocean)
    return board.get_or_create_credential(ocean, credential=credential)


@pytest.fixture(name="player_stock")
def fixture_player_stock(player: Player, stock: Stock) -> PlayerStock:
    player_stock = player.get_or_create_player_stock(stock)
    player_stock.amount = 1
    return player_stock


@pytest.fixture(name="player_etf")
def fixture_player_etf(player: Player, etf: ETF) -> PlayerStock:
    player_stock = player.get_or_create_player_stock(etf)
    player_stock.amount = 1
    return player_stock
