# 除錯模式
DEBUG_MODE: bool = True

# 玩家初始金額
PLAYER_DEFAULT_CASH: int = 3600

# 經過起點獲得的金額
PASS_START_POINT_CASH: int = 1000

# 增減存款格子的金額
CASH_SPACE_VALUE: int = 1000

# 相同區域每多擁有一個土地的加成
AREA_ADDITION_RATE: float = .25

# 是否可無限購買不動產
UNLIMITED_BUILDING: bool = True

# 可建造土地的建築上限(0-4)
BUILDING_UPPERBOUND: int = 4

# 賣掉土地的折現率
LAND_DISCOUNT_RATE: float = 1.

# 賣掉房子的折現率
HOUSE_DISCOUNT_RATE: float = .9

# 股票漲跌隨機值基數
STOCK_SHUFFLE_BASE: int = 100

# 遊戲狀態儲存資料夾
GAME_SAVE_FOLDER: str = "save"

# 遊戲狀態儲存副檔名
GAME_SAVE_SUFFIX: str = ".sav"
