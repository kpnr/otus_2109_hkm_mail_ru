"""Интерфейсы для работы с Аттракторами"""

from lesson3.interfaces import GenericInterface, abstractmethod

class AttractorExecInterface(GenericInterface):
    @abstractmethod
    def start(self, queue:CommandQueue):
        """Привязка очереди команд к Аттрактору"""