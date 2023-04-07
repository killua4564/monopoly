import abc
import contextlib
import pathlib
import time
import typing

from monopoly import configs
from monopoly.constants import BASE_DIR, SystemText

from .models import CancelableModelInterface, ShowableModelInterface


class BaseMenuInterface(CancelableModelInterface, abc.ABC):
    pass


class BasePropertyMenuInterface(BaseMenuInterface, ShowableModelInterface, abc.ABC):
    @property
    @abc.abstractmethod
    def sale_value(self) -> int:
        raise NotImplementedError


class BuildableMenuInterface(BasePropertyMenuInterface, abc.ABC):
    def construct_menu(self, player: "BasePlayer", board: "Board", *args, **kwargs):
        print(f"{player} 想要在 {self} 建造房屋嗎？")
        print("[B]uild")
        print("[I]nformation")
        print("[M]yself information")
        print("[C]ancel")

        command = input("> ").upper()
        if command == "B":
            self.construction(board, *args, **kwargs)
        elif command == "I":
            self.show()
        elif command == "M":
            player.show()
        else:
            raise self.Cancelled()

    @abc.abstractmethod
    def construction(self, board: "Board", *args, **kwargs):
        raise NotImplementedError

    def demolish_menu(self, player: "BasePlayer", board: "Board", *args, **kwargs):
        print(f"{player} 想要在 {self} 拆掉房屋嗎？")
        print("[D]emolish")
        print("[I]nformation")
        print("[M]yself information")
        print("[C]ancel")

        command = input("> ").upper()
        if command == "D":
            self.demolition(board, *args, **kwargs)
        elif command == "I":
            self.show()
        elif command == "M":
            player.show()
        else:
            raise self.Cancelled()

    @abc.abstractmethod
    def demolition(self, board: "Board", *args, **kwargs):
        raise NotImplementedError


class TradableMenuInterface(BasePropertyMenuInterface, abc.ABC):
    def buy_menu(self, player: "BasePlayer", board: "Board", *args, **kwargs):
        print(f"{player} 想要買入 {self} 嗎？")
        print("[B]uy")
        print("[I]nformation")
        print("[M]yself information")
        print("[C]ancel")

        command = input("> ").upper()
        if command == "B":
            self.buying(player, board, *args, **kwargs)
        elif command == "I":
            self.show()
        elif command == "M":
            player.show()
        else:
            raise self.Cancelled()

    @abc.abstractmethod
    def buying(self, player: "BasePlayer", board: "Board", *args, **kwargs):
        raise NotImplementedError

    def sell_menu(self, player: "BasePlayer", board: "Board", *args, **kwargs):
        print(f"{player} 想要賣出 {self} 嗎？")
        print("[S]ell")
        print("[I]nformation")
        print("[M]yself information")
        print("[C]ancel")

        command = input("> ").upper()
        if command == "S":
            self.selling(player, board, *args, **kwargs)
        elif command == "I":
            self.show()
        elif command == "M":
            player.show()
        else:
            raise self.Cancelled()

    @abc.abstractmethod
    def selling(self, player: "BasePlayer", board: "Board", *args, **kwargs):
        raise NotImplementedError


class EnginelizeMenuInterface(BaseMenuInterface, abc.ABC):
    def execute_menu(self, title: str, *args, **kwargs):
        print(f"[{title}]")
        print("[N]ew Game")
        print("[L]oad Game")
        print("[S]taff")
        print("[C]ancel to Exit")

        command = input("> ").upper()
        if command == "N":
            self.execution_new()
        elif command == "L":
            self.execution_load()
        elif command == "S":
            self.execution_staff()
        else:
            raise self.Cancelled()

    @abc.abstractmethod
    def execution_load(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def execution_new(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def execution_staff(self, *args, **kwargs):
        raise NotImplementedError


class PlayableMenuInterface(BaseMenuInterface, abc.ABC):
    @property
    @abc.abstractmethod
    def playable(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def playing(self, *args, **kwargs):
        raise NotImplementedError

    def play_menu(self, player: "BasePlayer", board: "Board", *args, **kwargs):
        print(f"{player} 請選擇要執行的動作")
        print("[D]ice to Play")
        print("[L]ands Information")
        print("[S]tocks Information")
        print("[P]layers Information")
        print("[T]rade-off Properties")
        print("[C]ancel to Surrender")
        print("[SAVE] Game")

        command = input("> ").upper()
        if command == "D":
            self.playing()
        elif command == "L":
            board.list_lands()
        elif command == "S":
            board.list_stocks()
        elif command == "P":
            board.list_players()
        elif command == "T":
            player.trade_off(board)
        elif command == "C":
            print(f"{player} 確定是否要投降？(Y/N)")
            if input("> ").upper() == "Y":
                player.surrender = True
                raise self.Cancelled()
        elif command == "SAVE":
            board.save()


class PropertyTradingOffMenuInterface(BaseMenuInterface, abc.ABC):
    def trade_off_menu(self, board: "Board", *args, **kwargs):
        print(f"{self} 想要變賣什麼呢？")
        print("[L]and & House")
        print("[S]tock")
        print("[C]ancel")

        command = input("> ").upper()
        if command == "L":
            self.trading_lands_off(board)
        elif command == "S":
            self.trading_stocks_off(board)
        else:
            raise self.Cancelled()

    @abc.abstractmethod
    def trading_lands_off(self, *args, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def trading_stocks_off(self, *args, **kwargs):
        raise NotImplementedError


class SavableMenuInterface(BaseMenuInterface, abc.ABC):
    SAVE_FOLDER: typing.ClassVar[str] = configs.GAME_SAVE_FOLDER
    SAVE_SUFFIX: typing.ClassVar[str] = configs.GAME_SAVE_SUFFIX

    @classmethod
    def _ensure_save_folder(cls, filename: str) -> pathlib.PosixPath:
        savepath: pathlib.PosixPath = BASE_DIR / cls.SAVE_FOLDER
        with contextlib.suppress(FileExistsError):
            savepath.mkdir()

        filepath: pathlib.PosixPath = savepath / filename
        if filepath.parent != savepath:
            raise FileNotFoundError()
        return filepath

    @classmethod
    def _ensure_suffix(cls, filename: str) -> str:
        if not filename.endswith(cls.SAVE_SUFFIX):
            return f"{filename}{cls.SAVE_SUFFIX}"
        return filename

    @classmethod
    def _get_saved_files(cls) -> typing.Generator[pathlib.PosixPath, None, None]:
        return (BASE_DIR / cls.SAVE_FOLDER).glob(f"*{cls.SAVE_SUFFIX}")

    @classmethod
    @abc.abstractmethod
    def loading(cls, filepath: pathlib.PosixPath, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def load_menu(cls, *args, **kwargs):
        print("請輸入加載的檔案名稱")
        for idx, file in enumerate(cls._get_saved_files(), 1):
            print(f"[{idx:02}] {file.name}")

        try:
            filename: str = cls._ensure_suffix(input("> "))
            return cls.loading(cls._ensure_save_folder(filename), *args, **kwargs)
        except FileNotFoundError:
            print(SystemText.FILENAME_ERROR.value)
        return None

    def auto_saving(self, *args, **kwargs):
        filename: str = f"_auto_saving_{int(time.time())}"
        filename = self._ensure_save_folder(self._ensure_suffix(filename))
        self.saving(filename, *args, **kwargs)

    @abc.abstractmethod
    def saving(self, filepath: pathlib.PosixPath, *args, **kwargs):
        raise NotImplementedError

    def save_menu(self, *args, **kwargs):
        print("請輸入儲存的檔案名稱")
        saved_files: tuple = tuple(self._get_saved_files())
        if saved_files:
            print("已儲存的檔案名稱:")
            for idx, file in enumerate(saved_files, 1):
                print(f"[{idx:02}] {file.name}")

        try:
            filename: str = self._ensure_suffix(input("> "))
            self.saving(self._ensure_save_folder(filename), *args, **kwargs)
        except FileNotFoundError:
            print(SystemText.FILENAME_ERROR.value)
