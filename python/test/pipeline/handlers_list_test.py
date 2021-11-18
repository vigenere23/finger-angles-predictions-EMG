from unittest import TestCase
from unittest.mock import MagicMock
from src.pipeline.handlers import DataHandler, HandlersList


class MockedHandler(DataHandler):
    def __init__(self, receiver):
        super().__init__()
        self.handle = receiver

    def handle(self, _):
        pass


class Transferer(DataHandler):
    def handle(self, input):
        self._next(input)


class ConditionalHandlerTest(TestCase):
    SOME_VALUE = 1

    def test_it_passes_input_to_first_child(self):
        child = MockedHandler(MagicMock())
        handler = HandlersList([child])

        handler.handle(self.SOME_VALUE)

        child.handle.assert_called_once_with(self.SOME_VALUE)

    def test_children_are_chained(self):
        first_child = Transferer()
        second_child = MockedHandler(MagicMock())
        handler = HandlersList([first_child, second_child])

        handler.handle(self.SOME_VALUE)

        second_child.handle.assert_called_once_with(self.SOME_VALUE)
