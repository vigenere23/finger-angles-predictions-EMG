from src.pipeline.executors.base import Executor, ExecutorFactory, FromSourceExecutor, Retryer
from src.pipeline.handlers import DataHandler
from src.pipeline.sources import FrequencyConfig, RandomSource, FrequencySource, SerialSource
from src.utils.loggers import ConsoleLogger


class SerialExecutorFactory(ExecutorFactory):
    def __init__(self, port: str, output_handler: DataHandler) -> None:
        self.__output_handler = output_handler

        logger = ConsoleLogger(prefix="[serial]")

        if port == 'rand':
            self.__source = RandomSource()
        elif 'freq' in port:
            try:
                configs = []
                for config in port.split(':')[1].split('_'):
                    amp, freq, offset = config.split('-')
                    configs.append(
                        FrequencyConfig(
                            amplitude=float(amp),
                            frequency=float(freq),
                            offset=float(offset))
                    )
                self.__source = FrequencySource(configs=configs)
            except KeyError:
                raise ValueError("format should be 'freq:<amp1-freq1-offset1>_<amp2-freq2-offset2>_<...>'")
        else:
            self.__source = SerialSource(
                port=port,
                baudrate=115200,
                sync_byte=b'\n',
                check_byte=b'\xFF',
                logger=logger,
                # verbose=True
            )
        
    def create(self) -> Executor:
        executor = FromSourceExecutor(source=self.__source, handler=self.__output_handler)
        executor = Retryer(executor=executor, nb_retries=10)

        return executor
