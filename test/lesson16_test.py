"""Тесты для автогенератора Адаптеров
"""

from abc import abstractmethod
import pytest
from lesson16.implementations import adapter_factory_register, InterfaceToAdapter
from lesson14.interfaces import IoCController
from lesson14.implementations import SimpleIoC
from lesson3.interfaces import GenericInterface, UObject


class SomeInterface(GenericInterface):
    """Проверка концепта - интерфейс"""

    @abstractmethod
    def method1(self) -> str:
        """Тестовый метод 1"""

    @abstractmethod
    def method2(self, b: int) -> str:
        """Тестовый метод 2"""


# noinspection PyAbstractClass
class SomeAdapter(SomeInterface, InterfaceToAdapter):
    """Проверка концепта - адаптер"""


ioc: IoCController = SimpleIoC()  # Используется Адаптерами, созданными в данном модуле


def _ioc_init(methods):
    global ioc
    ioc = SimpleIoC()
    adapter_factory_register(ioc)
    for k, v in methods.items():
        ioc.resolve('ioc.register', k, v)
    return


# методы для реализации SomeInterface для загрузки в UObject
some_interface_imp = {
    'lesson16_test.SomeInterface:method1': lambda u_obj: u_obj.test_value,
    'lesson16_test.SomeInterface:method2': lambda u_obj, count: u_obj.test_value * count
    }


def test_interface_to_adapter():
    """Тест, что в результате получен адаптер, поддерживающий нужный интерфейс"""
    u_obj = UObject()
    with pytest.raises(AttributeError):
        SomeAdapter._assert_support(u_obj)
    some_adapter: SomeInterface = SomeAdapter(u_obj, ioc)
    SomeAdapter._assert_support(some_adapter)


def test_adapter_imp():
    """Тест реализации адаптера - взаимодействие с ioc и вызов функций,
    загруженных в ioc
    """
    _ioc_init(some_interface_imp)
    u_obj = UObject(test_value='test_value ')
    some_adapter = SomeAdapter(u_obj, ioc)
    m1 = some_adapter.method1
    assert m1() == 'test_value '
    m2 = some_adapter.method2
    assert m2(2) == 'test_value test_value '


def test_ioc_factory():
    """Тест создания адаптера через ioc"""
    _ioc_init(some_interface_imp)
    u_obj = UObject(test_value='test_value ')
    some_adapter = ioc.resolve('Adapter', SomeInterface, u_obj, ioc)
    m1 = some_adapter.method1
    assert m1() == 'test_value '
    m2 = some_adapter.method2
    assert m2(2) == 'test_value test_value '


# noinspection PyArgumentList
def test_adapter_params():
    """Тест контроля количества параметров для созданного Адаптера"""
    _ioc_init(some_interface_imp)
    u_obj = UObject(test_value='test_value ')
    some_adapter = SomeAdapter(u_obj, ioc)
    with pytest.raises(TypeError):
        some_adapter.method1('raise')
    with pytest.raises(TypeError):
        some_adapter.method2()
