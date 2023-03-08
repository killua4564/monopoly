import abc
import re
import typing

import pydantic


class BaseModelInterface(pydantic.BaseModel, abc.ABC):
    pass


class CancelableModelInterface(BaseModelInterface, abc.ABC):
    class Cancelled(Exception):
        pass


class ChainableInterface(BaseModelInterface, abc.ABC):
    backwards: typing.Union["ChainableInterface", None] = None
    forwards: typing.Union["ChainableInterface", None] = None

    def chain(self, other: "ChainableInterface"):
        self.set_forwards(other)
        other.set_backwards(self)

    @abc.abstractmethod
    def get_backwards(self) -> typing.Union["ChainableInterface", None]:
        raise NotImplementedError

    @abc.abstractmethod
    def get_forwards(self) -> typing.Union["ChainableInterface", None]:
        raise NotImplementedError

    @abc.abstractmethod
    def set_backwards(self, other: "ChainableInterface"):
        raise NotImplementedError

    @abc.abstractmethod
    def set_forwards(self, other: "ChainableInterface"):
        raise NotImplementedError


class BaseViewableModelInterface(BaseModelInterface, abc.ABC):
    CHINESE_RE: str = r"[\u4e00-\u9fff]"

    def chinese_length(self, data: typing.Any) -> int:
        return len(re.findall(self.CHINESE_RE, str(data)))


class ShowableModelInterface(BaseViewableModelInterface, abc.ABC):
    _width: int = 26

    @classmethod
    def print_row(cls, data: str):
        print(f"|{data}|")

    @abc.abstractmethod
    def show(self, *args, **kwargs):
        raise NotImplementedError

    def show_divider(self):
        print("+" + "-" * self._width + "+")

    def show_horizontal(self):
        self.print_row(" " * self._width)
