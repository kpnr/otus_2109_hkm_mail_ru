"""Тесты для урока № 14"""
from typing import Any
from time import sleep
from random import random
from threading import Thread
from pytest import raises
from lesson14.implementations import (
    SimpleIoC, IoCController, PolymorphIoC, ThreadSafeIoC, ThreadLocalIoC)


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


def test_thread_safe_ioc():
    def SlowMethod() -> None:
        nonlocal shared_value
        local_value = shared_value
        sleep(0.1 + random())  # сделаем паузу между чтением и записью
        shared_value = local_value + 1

    def thread_runner():
        """Выполняется в отдельном потоке"""
        ioc.resolve('test')

    shared_value = 0
    thread_count = 10
    ioc = ThreadSafeIoC()
    ioc.resolve('ioc.register', 'test', SlowMethod)
    threads = [Thread(target=thread_runner) for _ in range(thread_count)]
    for x in threads:  # Устроим гонки вокруг разделяемой переменной
        x.start()
    for x in threads:  # Подождем всех участников
        x.join()
    # Проверим, что гонки не привели к повреждению ресурса
    assert shared_value == thread_count


def test_thread_local_ioc():
    def thread_runner(uniq_arg: int):
        """Выполняется в отдельном потоке"""
        nonlocal is_ok
        ioc.resolve('ioc.register', 'test', lambda : uniq_arg * 2)
        # Пауза
        sleep(random())
        # И проверка, что наша зависимость не испорчена другим потоком
        processed_arg = ioc.resolve('test')
        if processed_arg != uniq_arg * 2:
            is_ok = False

    ioc = ThreadLocalIoC()
    thread_count = 10
    is_ok = True
    threads = [Thread(target=thread_runner, args=[x])
               for x in range(thread_count)]
    for x in threads:  # Устроим гонки вокруг общего IoC
        x.start()
    for x in threads:  # Подождем всех участников
        x.join()
    assert is_ok

