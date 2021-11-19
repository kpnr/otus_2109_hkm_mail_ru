"""Тесты для урока № 14"""
from typing import Any
from pytest import raises
from lesson14.implementations import SimpleIoC, IoCController, PolymorphIoC


def test_simple_ioc():
    def _found(value):
        nonlocal test_value
        test_value = value
        return value

    test_value = 0
    ioc = SimpleIoC()
    with raises(Exception):
        ioc.resolve('not_found')
    ioc.resolve('ioc.register', 'found', _found)
    assert ioc.resolve('found', 11) == 11
    assert test_value == 11


def test_polymorph_ioc():
    # noinspection PyMissingOrEmptyDocstring
    class DummyIoC(IoCController):
        def resolve(self, key: str, *args, **kwargs) -> Any:
            raise NotImplementedError('')

    ioc = PolymorphIoC()
    ioc.resolve('ioc.register', 'test', lambda : 11)
    assert ioc.resolve('test') == 11
    ioc.resolve('ioc.replace', SimpleIoC())
    with raises(Exception):
        ioc.resolve('test')
    with raises(NotImplementedError):
        ioc.resolve('ioc.replace', DummyIoC())
