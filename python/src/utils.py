from typing import Generic, TypeVar


ListItem = TypeVar('ListItem', float, int)


class SizedFifo(Generic[ListItem]):
    def __init__(self, size: int):
        self.__list = [0] * size

    def append(self, item: ListItem):
        self.__list.append(item)
        self.__list.pop(0)

    def oldest(self):
        return self.__list[0]

    def newest(self):
        return self.__list[-1]
