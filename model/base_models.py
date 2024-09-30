from abc import ABC,abstractmethod

class have_dict(ABC):
    @abstractmethod
    def to_dict(self) -> dict:
        pass