#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import logging.handlers


def init_logger(log_file, logger_name="", log_level=logging.DEBUG, max_bytes=100 * 1024 * 1024, backup_count=5):
    fmt = "%(asctime)s [%(filename)s:%(lineno)s] [%(name)s] [%(levelname)s] %(message)s"
    formatter = logging.Formatter(fmt)

    fhandler = logging.handlers.RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
    fhandler.setFormatter(formatter)

    shandler = logging.StreamHandler()
    shandler.setFormatter(formatter)

    logger = logging.getLogger(logger_name)
    logger.addHandler(fhandler)
    logger.addHandler(shandler)
    logger.setLevel(log_level)
    return logger
