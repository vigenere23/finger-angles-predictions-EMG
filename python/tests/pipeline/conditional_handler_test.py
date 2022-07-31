from unittest import TestCase
from unittest.mock import MagicMock

from src.pipeline.handlers import Condition, ConditionalHandler, DataHandler


class TrueCondition(Condition):
    def check(self, _) -> bool:
        return True


class FalseCondition(Condition):
    def check(self, _) -> bool:
        return False


class MockedHandler(DataHandler):
    def __init__(self, receiver):
        super().__init__()
        self.handle = receiver

    def handle(self, _):
        pass


class Transferer(DataHandler):
    def handle(self, input):
        self._next(input)


class Modifier(DataHandler):
    def handle(self, _):
        self._next(None)


class ConditionalHandlerTest(TestCase):
    SOME_VALUE = 1

    def test_given_true_condition_it_passes_input_to_child(self):
        child = MockedHandler(MagicMock())
        handler = ConditionalHandler(condition=TrueCondition(), child=child)

        handler.handle(self.SOME_VALUE)

        child.handle.assert_called_once_with(self.SOME_VALUE)

    def test_given_true_condition_it_passes_input_to_next(self):
        child = Modifier()
        next = MockedHandler(MagicMock())
        handler = ConditionalHandler(condition=TrueCondition(), child=child)
        handler.set_next(next)

        handler.handle(self.SOME_VALUE)

        next.handle.assert_called_once_with(self.SOME_VALUE)

    def test_given_false_condition_it_does_not_pass_input_to_child(self):
        child = MockedHandler(MagicMock())
        handler = ConditionalHandler(condition=FalseCondition(), child=child)

        handler.handle(self.SOME_VALUE)

        child.handle.assert_not_called()

    def test_given_false_condition_it_passes_input_to_next(self):
        child = Modifier()
        next = MockedHandler(MagicMock())
        handler = ConditionalHandler(condition=TrueCondition(), child=child)
        handler.set_next(next)

        handler.handle(self.SOME_VALUE)

        next.handle.assert_called_once_with(self.SOME_VALUE)
