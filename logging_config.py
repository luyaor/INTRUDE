import logging
import logging.handlers
import os

LEVELS = {'NOSET': logging.NOTSET,
          'DEBUG': logging.DEBUG,
          'INFO': logging.INFO,
          'WARNING': logging.WARNING,
          'ERROR': logging.ERROR,
          'CRITICAL': logging.CRITICAL}

# create logs file folder
logs_dir = os.path.join(os.path.curdir, "logs")
if os.path.exists(logs_dir) and os.path.isdir(logs_dir):
    pass
else:
    os.mkdir(logs_dir)
  
# define a rotating file handler
rotatingFileHandler = logging.handlers.RotatingFileHandler(filename ="./logs/log.txt", maxBytes = 1024 * 1024 * 500, backupCount = 5)

formatter = logging.Formatter("%(asctime)s %(name)-12s %(levelname)-8s %(message)s")

rotatingFileHandler.setFormatter(formatter)

logging.getLogger("").addHandler(rotatingFileHandler)

#define a handler whitch writes messages to sys

console = logging.StreamHandler()

console.setLevel(logging.NOTSET)

#set a format which is simple for console use

formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")

#tell the handler to use this format

console.setFormatter(formatter)

#add the handler to the root logger

logging.getLogger("").addHandler(console)

# set initial log level
logger = logging.getLogger("")
logger.setLevel(logging.WARNING) 

