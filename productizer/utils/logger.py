from starlette.types import ASGIApp, Receive, Scope, Send

from logging import config as logging_configurator, Logger

logging_configurator.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",  # Default is stderr
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["default"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }
)


class LoggingMiddleware:
    def __init__(self, app: ASGIApp, logger: Logger) -> None:
        self.app = app
        self.logger = logger

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        self.logger.info("%s %s", scope["method"], scope["path"])
        await self.app(scope, receive, send)
