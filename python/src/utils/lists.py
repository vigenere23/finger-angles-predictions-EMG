from typing import Generic, List, TypeVar


ListItem = TypeVar('ListItem', float, int)


class SizedFifo(Generic[ListItem]):
    def __init__(self, size: int):
        self.__size = size
        self.__list = [0] * size

    def append(self, item: ListItem):
        self.__list.append(item)
        self.__list.pop(0)

    def add_all(self, items: List[ListItem]):
        self.__list.extend(items)
        self.__list = self.__list[-self.__size:]

    def to_list(self) -> List[ListItem]:
        return self.__list

    def oldest(self):
        return self.__list[0]

    def newest(self):
        return self.__list[-1]
