import pytest

from monopoly.engines import BaseEngine, StandAloneEngine


@pytest.fixture(name="engine")
def fixture_engine() -> BaseEngine:
    return StandAloneEngine()


@pytest.fixture(name="stand_alone_engine")
def fixture_stand_alone_engine() -> StandAloneEngine:
    return StandAloneEngine()
