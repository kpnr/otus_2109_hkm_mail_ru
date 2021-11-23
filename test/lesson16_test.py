"""Тесты для автогенератора Адаптеров
"""

import pytest
from lesson16.implementations import interface_to_adapter, SomeInterface

def test_interface_to_adapter():
    interface_to_adapter(SomeInterface)
