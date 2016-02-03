import sys
import logging
try:
    import coloredlogs
except ImportError:
    pass


def setupLogger(filename, loglevel_file, loglevel_stderr):
    if filename is not None:
        fmt = '%(asctime)s [%(levelname)s] %(message)s'
        date_fmt = '%Y-%m-%d %H:%M'

        try:
            consoleFormatter = coloredlogs.ColoredFormatter(fmt, date_fmt)
        except NameError:
            consoleFormatter = logging.Formatter(fmt, date_fmt)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(loglevel_stderr)
        consoleHandler.setFormatter(consoleFormatter)

        fileFormatter = logging.Formatter(fmt, date_fmt)
        fileHandler = logging.FileHandler(filename)
        fileHandler.setLevel(loglevel_file)
        fileHandler.setFormatter(fileFormatter)

        logging.getLogger().setLevel(0)
        logging.getLogger().addHandler(fileHandler)
        logging.getLogger().addHandler(consoleHandler)
    else:
        try:
            coloredlogs.install(fmt=fmt, datefmt=date_fmt, level=loglevel_stderr)
        except NameError:
            logging.basicConfig(format=fmt, datefmt=date_fmt, level=loglevel_stderr)

def toBool(obj):
    if type(obj) is bool:
        return bool
    elif type(obj) is str:
        return obj.lower() == 'true'
    else:
        raise TypeError('Argument has to be Boolean or String')

