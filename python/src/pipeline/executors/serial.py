from typing import List
from src.pipeline.executors.base import Executor, ExecutorFactory, HandlersExecutor, Retryer
from src.pipeline.handlers import DataHandler
from src.pipeline.sources import FrequencyConfig, RandomSource, FrequencySource, SerialSource
from src.utils.loggers import ConsoleLogger


class SerialExecutorFactory(ExecutorFactory):
    def __init__(self, port: str, output_handlers: List[DataHandler]) -> None:
        logger = ConsoleLogger(prefix="[serial]")

        if port == 'rand':
            self.__source = RandomSource()
        elif 'freq' in port:
            try:
                configs = []
                for config in port.split(':')[1].split('_'):
                    amp, freq = config.split('-')
                    configs.append(
                        FrequencyConfig(
                            amplitude=int(amp),
                            frequency=int(freq))
                    )
                self.__source = FrequencySource(configs=configs)
            except KeyError:
                raise ValueError("format should be 'freq:<amp1-freq1>_<amp2-freq2>_<...>'")
        else:
            self.__source = SerialSource(
                port=port,
                baudrate=115200,
                sync_byte=b'\n',
                check_byte=b'\xFF',
                # use_parity=True, TODO parity not working
                logger=logger,
                # verbose=True
            )

        self.__output_handlers = output_handlers
        
    def create(self) -> Executor:
        handlers = [
            *self.__output_handlers,
        ]

        executor = HandlersExecutor(source=self.__source, handlers=handlers)
        executor = Retryer(executor=executor, nb_retries=10)

        return executor
