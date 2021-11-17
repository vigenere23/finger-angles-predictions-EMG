from typing import Iterator, List
from unittest import TestCase
import unittest
from unittest.mock import MagicMock
from src.pipeline.handlers import BranchedHandler, BranchingCondition, DataHandler


class AlwaysTrueCondition(BranchingCondition):
    def check(self, _) -> bool:
        return True


class AlwaysFalseCondition(BranchingCondition):
    def check(self, _) -> bool:
        return False


class Transformer(DataHandler):
    def handle(self, input: Iterator) -> Iterator:
        for _ in input:
            yield None


class Transferer(DataHandler):
    def __init__(self, receiver):
        self.receiver = receiver

    def handle(self, input: Iterator) -> Iterator:
        for data in input:
            self.receiver(data)
            yield data


class BranchedHandlers2Test(TestCase):
    A_VALUE = 1
    ANOTHER_VALUE = 2

    def test_it_yields_original_data_to_sibling(self):
        handler = create_branched_handler()
        iterator = chain_handlers([self.A_VALUE, self.ANOTHER_VALUE], [handler])

        returned_value1, returned_value2 = next(iterator), next(iterator)

        self.assertEqual(returned_value1, self.A_VALUE)
        self.assertEqual(returned_value2, self.ANOTHER_VALUE)

    def test_it_sends_transformed_data_to_children(self):
        receiver = MagicMock()
        handler = create_branched_handler(receiver=receiver)
        iterator = chain_handlers([self.A_VALUE], [handler])

        next(iterator)

        receiver.assert_called_with(None)

    def test_it_calls_each_children_once(self):
        receiver = MagicMock()
        handler = create_branched_handler(receiver=receiver)
        iterator = chain_handlers([self.A_VALUE], [handler])

        next(iterator)

        receiver.assert_called_once()

    def test_given_multiple_in_chain_it_should_not_recall_parents(self):
        receiver_1 = MagicMock()
        receiver_2 = MagicMock()
        handler_1 = create_branched_handler(receiver=receiver_1)
        handler_2 = create_branched_handler(receiver=receiver_2)
        iterator = chain_handlers([self.A_VALUE], [handler_1, handler_2])

        next(iterator)

        receiver_1.assert_called_once()
        receiver_2.assert_called_once()

    def test_when_reaching_end_of_iterator_it_should_Raise_StopIteration_error(self):
        handler = create_branched_handler()
        iterator = chain_handlers([self.A_VALUE], [handler])

        next(iterator)
        self.assertRaises(StopIteration, lambda: next(iterator))

    def test_given_sibling_of_other_type_it_should_not_reiterate(self):
        handler = create_branched_handler()
        iterator = chain_handlers([self.A_VALUE], [handler, Transformer()])

        next(iterator)

    def test_given_condition_False_it_should_not_reiterate(self):
        handler = create_branched_handler(condition=AlwaysFalseCondition())
        iterator = chain_handlers([self.A_VALUE], [handler, Transformer()])

        next(iterator)


def chain_handlers(iterator: Iterator, handlers: List[DataHandler]) -> Iterator:
    for handler in handlers:
        iterator = handler.handle(iterator)
    
    return iterator


def create_branched_handler(condition: BranchingCondition = AlwaysTrueCondition(), receiver = lambda _: None):
    return BranchedHandler(condition=condition, handlers=[Transformer(), Transferer(receiver)])


if __name__ == '__main__':
    unittest.main()
