import contextlib
import csv
import random

import pydantic

from monopoly.constants import Area, CardType, CashType, FixturePath, SystemText
from monopoly.models.boards import Board, BoardPlayer, BoardSpace
from monopoly.models.equipments import cards as card_models
from monopoly.models.equipments import spaces as space_models
from monopoly.models.equipments.players import Player
from monopoly.models.properties.lands import Land, Ocean
from monopoly.models.properties.stocks import ETF, Stock

from .base import BaseLoader


class FixtureLoader(BaseLoader):
    def load_cards(self, board: Board):
        with open(FixturePath.CARDS.value, "r", encoding="utf-8") as file:
            for data in csv.DictReader(file):
                data["card_type"] = CardType[data["card_type"]]
                if data["cash_type"]:
                    data["cash_type"] = CashType[data["cash_type"]]

                board.cards[data["card_type"]].append(
                    getattr(card_models, data["cls"]).parse_obj(data),
                )

    def load_etfs(self, board: Board):
        with open(FixturePath.ETFS.value, "r", encoding="utf-8") as file:
            etfs = {}
            for data in csv.DictReader(file):
                key = data["id"]
                etf = ETF.parse_obj(data)

                stocks = board.stocks.values()
                for cond in data["filters"].split(","):
                    if not cond:
                        continue

                    with contextlib.suppress(ValueError):
                        stocks = [
                            stock
                            for stock in stocks
                            if stock.land.area == Area(cond)
                        ]
                        continue

                    field, number = cond.split("|")
                    reverse, number = int(number) > 0, abs(int(number))
                    if field == "市值":
                        stocks = sorted(
                            stocks,
                            key=lambda stock: stock.amount * stock.value,
                            reverse=reverse,
                        )[:number]
                    elif field == "低波動":
                        stocks = sorted(
                            stocks,
                            key=lambda stock: -stock.beta,
                            reverse=reverse,
                        )[:number]
                    elif field == "ESG":
                        stocks = sorted(
                            stocks,
                            key=lambda stock: stock.esg_ratio,
                            reverse=reverse,
                        )[:number]
                    elif field == "高股息":
                        stocks = sorted(
                            stocks,
                            key=lambda stock: stock.payout_ratio,
                            reverse=reverse,
                        )[:number]

                if data["index"] == "市值":
                    summarize = sum(stock.amount * stock.value for stock in stocks)
                    for stock in sorted(
                        stocks,
                        key=lambda stock: stock.amount * stock.value,
                        reverse=True,
                    ):
                        etf.constituents.append(ETF.Constituent(
                            stock=stock,
                            percent=stock.amount * stock.value / summarize,
                        ))
                elif data["index"] == "高股息":
                    summarize = sum(stock.payout_ratio for stock in stocks)
                    for stock in sorted(
                        stocks,
                        key=lambda stock: stock.payout_ratio,
                        reverse=True,
                    ):
                        etf.constituents.append(ETF.Constituent(
                            stock=stock,
                            percent=stock.payout_ratio / summarize,
                        ))

                etf.reset()
                etfs[key] = etf
            board.stocks.update(etfs)

    def load_lands(self, board: Board):
        with open(FixturePath.LANDS.value, "r", encoding="utf-8") as file:
            for data in csv.DictReader(file):
                key = data["id"]
                if data["area"] == Area.OCEAN.value:
                    data["tolls"] = (data["land_price"],)
                    land = Ocean.parse_obj(data)
                    board.lands[key] = land
                    continue

                data["tolls"] = tuple(data["tolls"].split(","))
                data["value"] = data["land_price"]
                land = Land.parse_obj(data)
                stock = Stock.parse_obj(data)
                stock.land, land.stock = land, stock
                board.lands[key], board.stocks[key] = land, stock

    def load_players(self, board: Board):
        number = 2
        players = []
        with contextlib.suppress(ValueError):
            print("有幾個人要玩遊戲呢？(2+)")
            number = max(int(input("> ")), number)

        player_names: set[str] = set()
        for idx in range(1, number+1):
            while True:
                try:
                    print(f"請輸入第{idx}位玩家名稱(長度限制1-6個字):")
                    player = Player(name=input("> "))
                    assert player.name not in player_names
                    player_names.add(player.name)
                    break
                except (AssertionError, pydantic.error_wrappers.ValidationError):
                    print(SystemText.NAME_ERROR.value)

            players.append(BoardPlayer(board=board, player=player))

        board.start_player = players[0]
        for player, other in zip(players, players[1:] + [players[0]]):
            player.chain(other)

    def load_stocks(self, board: Board):
        # Stocks have loaded in lands.csv
        # Learing With Errors
        for stock in board.stocks.values():
            stock.beta += random.randint(-5, 5) / 100
            stock.esg_ratio += random.randint(-5, 5) / 100
            stock.payout_ratio += random.randint(-5, 5) / 100

    def load_spaces(self, board: Board):
        with open(FixturePath.SPACES.value, "r", encoding="utf-8") as file:
            spaces, directions = {}, {}
            for data in csv.DictReader(file):
                key = data["id"]
                if data["cls"] == "LandSpace":
                    data["name"] = board.lands[key].name
                    data["land"] = data["ocean"] = board.lands[key]
                elif data["cls"] == "CardSpace":
                    data["name"] = CardType[key[:-2]]
                elif data["cls"] == "CashSpace":
                    data["name"] = CashType[key[:-2]]

                spaces[key] = BoardSpace(
                    board=board,
                    space=getattr(space_models, data["cls"]).parse_obj(data)
                )

                directions[key] = tuple(map(
                    lambda x: x.split(","),
                    (data["_backwards"], data["_forwards"]),
                ))

            for key, (backwards, forwards) in directions.items():
                for backward in backwards:
                    spaces[key].set_backwards(spaces[backward])
                for forward in forwards:
                    spaces[key].set_forwards(spaces[forward])

            board.start_space = spaces["STARTPOINT"]
