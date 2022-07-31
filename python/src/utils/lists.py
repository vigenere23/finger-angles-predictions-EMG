from typing import Generic, Iterator, List, TypeVar

ListItem = TypeVar("ListItem")


class SizedFifo(Generic[ListItem]):
    def __init__(self, size: int):
        self.__size = size
        self.__list = [0] * size

    def append(self, item: ListItem):
        self.__list.append(item)
        del self.__list[0]

    def add_all(self, items: List[ListItem]):
        self.__list.extend(items)
        self.__list = self.__list[-self.__size :]

    def to_list(self) -> List[ListItem]:
        return self.__list

    def oldest(self):
        return self.__list[0]

    def newest(self):
        return self.__list[-1]


def iter_groups(list: List[ListItem], group_size: int) -> Iterator[List[ListItem]]:
    generator = (
        list[index : index + group_size] for index in range(0, len(list), group_size)
    )
    for group in generator:
        yield group
