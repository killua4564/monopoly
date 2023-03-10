import enum
import os
import pathlib

BASE_DIR: pathlib.PosixPath = pathlib.Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Area(str, enum.Enum):
    BLUE = "BLUE"
    BROWN = "BROWN"
    COFFEE = "COFFEE"
    GREEN = "GREEN"
    GREENBLACK = "GREENBLACK"
    OCEAN = "OCEAN"
    ORANGE = "ORANGE"
    PURPLE = "PURPLE"
    RED = "RED"


class CardType(str, enum.Enum):
    CHANCE = "機會卡片"
    COMMUNITY_CHEST = "命運卡片"


class CashType(str, enum.Enum):
    EARNING = "賺取金額"
    COSTING = "損失金額"


class DirectionAttr(str, enum.Enum):
    BACKWARDS = "get_backwards"
    FORWARDS = "get_forwards"


class FixturePath(str, enum.Enum):
    CARDS = "fixtures/cards.csv"
    ETFS = "fixtures/etfs.csv"
    LANDS = "fixtures/lands.csv"
    SPACES = "fixtures/spaces.csv"


class StockType(str, enum.Enum):
    ETF = "etf"
    STOCK = "stock"


class SystemText(str, enum.Enum):
    BUYING_SUCCESS = "購買成功!!"
    CONSTRUCTION_SUCCESS = "建造成功!!"
    DEMOLITION_SUCCESS = "拆除成功!!"
    FILENAME_ERROR = "檔案名稱錯誤!!"
    GAME_OVER = "遊戲結束!!"
    GAME_STAFF = "\n".join((
        "Staff: Quack Lu (killua4564)",
        "Staff: Dubbit (dubbit0923)",
        "BGM: https://youtu.be/DSG53BsUYd0",
    ))
    GAME_TITLE = "肥嫩大富翁"
    LISTABLE_CANCEL = "取消請輸入 [C]ancel"
    LOADING_FAILED = "加載失敗!!"
    NAME_ERROR = "名稱錯誤!!"
    OPENING_STOCKS = "股票開市!!"
    PAUSE_SPACE_NAME = "暫停乙次"
    PRESS_ENTER_TO_CONTINUE = "> Press enter to continue..."
    PROPERTY_CODE_ERROR = "代碼錯誤!!"
    REVERSE_FINISH = "翻轉完成!!"
    SELLING_SUCCESS = "賣出成功!!"
    START_POINT_NAME = "臺灣起點"
    THREE_DICES_NAME = "骰子x3"
    TRANSPORT_FINISH = "傳送完成!!"
    TRANSPORT_START_POINT_NAME = "傳送起點"
    UNDEFINED = "NULL"
    UNEXPECTED_ERROR = "出現非預期錯誤"


class TaxFee(float, enum.Enum):
    ETF_TRANSFER_TAX = .001
    FORECLOSE_FEE = .8
    HOUSE_TAX = .03
    IMPOSE_FEE = 1.1
    INCOMING_TAX = .05
    LAND_VALUE_TAX = .01
    STOCK_HANDLING_FEE = .001425
    STOCK_TRANSFER_TAX = .003
