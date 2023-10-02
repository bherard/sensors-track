#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""loggin.py: Sesnors medation logging utils"""

# --------------------------------------------------------
# Software Name : Sensor Track
#
# 2023 Orange
#
# -------------------------------------------------------
#   Benoit HERARD <benoit.herard(at)orange.com>
# -------------------------------------------------------
import json
import logging
import logging.config

from pythonjsonlogger.jsonlogger import JsonFormatter

class AppJsonFormatter(JsonFormatter):
    """JSON Formatter for Application logs."""
    def __init__(self,  format, version, **kwargs):  # pylint: disable=redefined-builtin
        """Create an AppJsonFormatter instance.

        :param format: Log format
        :type format: str
        :param version: Software version to include in log
        :type version: str
        """
        super().__init__((format), **kwargs)
        self.static_fields["type"] = "APP"
        self.static_fields["version"] = version


class LoggingConfig:
    """Logging configuration utility class."""

    @staticmethod
    def _disable_stdout(logger):
        hdlrs_to_remove = []
        for hdlr in  logger.handlers:
            if "stream" in dir(hdlr) \
                and "name" in dir(hdlr.stream) \
                and hdlr.stream.name in  ["<stdout>", "<stderr>"]:
                hdlrs_to_remove.append(hdlr)
        for hdlr in hdlrs_to_remove:
            logger.removeHandler(hdlr)

    # pylint: disable=too-many-arguments
    @staticmethod
    def configure_logging(
            conf,
            logging_config_file,
            version,
        ):
        """Configure logging lib.

        :param conf: Runtime configuration dict
        :type conf: dict
        :param logging_config_file: Logging lib config file
        :type logging_config_file: str
        :param version: Software version to include in logs
        :type version: str

        Example of config dict

        .. code-block:: json

            {
                "logging": {
                    "level": "DEBUG",
                    "enable_stdout_stderr": false,
                    "file": "/tmp/my-app.log",
                    "file_size_M": 100,
                    "rotation_count": 5
                }
            }

        **Optional configuration keys:**

        * ``enable_stdout_stderr`` If set to true console logger is enabled (default true)
        * ``format`` Default is ``text``, can be set to ``json``
        """
        with open(logging_config_file, encoding="utf-8") as json_file:
            logging_config = json.load(json_file)
        fmt = "text"
        if "format" in conf["logging"]:
            fmt = conf["logging"]["format"]
        for formatter in logging_config["formatters"]:
            logging_config["formatters"][formatter]["version"] = version
        # configure default logging
        log_file_conf = logging_config["handlers"]["file_rotating"]
        if "file" in conf["logging"]:
            log_file_conf["filename"] = conf["logging"]["file"]
            log_file_conf["backupCount"] = conf["logging"]["rotation_count"]
            log_file_conf["maxBytes"] = conf["logging"]["file_size_M"] * 1024 * 1024
        else:
            log_file_conf["filename"] = "/dev/null"
            log_file_conf["backupCount"] = 0
            log_file_conf["maxBytes"] = 0


        #Set format for app logger
        logging_config["handlers"]["console"]["formatter"] = F"console_{fmt}"
        logging_config["handlers"]["file_rotating"]["formatter"] = F"file_{fmt}"


        logging.config.dictConfig(
            logging_config
        )
        # logging.config.fileConfig(
        #     logging_config_file,
        #     disable_existing_loggers=False  # To avoid sub thread disabling loggers when stating
        # )

        logging.getLogger().setLevel(
            logging.getLevelName(
                conf["logging"]["level"].upper()
            )
        )

        #Disable some handler according to conf
        if "enable_stdout_stderr" in conf["logging"] and \
            not conf["logging"]["enable_stdout_stderr"]:
            # Remove console for root logger
            LoggingConfig._disable_stdout(logging.getLogger())
