from abc import ABC,abstractmethod

from pyasn1.compat.octets import str2octs

class have_dict(ABC):

    uuid: str

    @abstractmethod
    def to_dict(self) -> dict:
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        pass