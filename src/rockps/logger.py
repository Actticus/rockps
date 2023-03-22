import logging
import sys

import loguru

from rockps import settings


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: 'CRITICAL',
        40: 'ERROR',
        30: 'WARNING',
        20: 'INFO',
        10: 'DEBUG',
        0: 'NOTSET',
    }

    def emit(self, record):
        try:
            level = loguru.logger.level(record.levelname).name
        except AttributeError:
            level = self.loglevel_mapping[record.levelno]

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        log = loguru.logger.bind(request_id='app')
        log.opt(
            depth=depth,
            exception=record.exc_info
        ).log(
            level,
            record.getMessage()
        )


def setup():
    loguru.logger.remove()
    loguru.logger.add(
        sys.stdout,
        enqueue=True,
        colorize=True,
        backtrace=True,
        diagnose=False,
        level=settings.LOG_CONFIG["level"],
        format=settings.LOG_CONFIG["format"],
    )
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    for _log in settings.LOG_CONFIG["loggers"]:
        _logger = logging.getLogger(_log)
        _logger.handlers = [InterceptHandler()]
