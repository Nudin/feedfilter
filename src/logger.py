#
#  feedfilter - remove duplicates and uninteresting stuff in news-feeds
#  Copyright (C) 2016 Michael F. Schoenitzer
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging

try:
    import coloredlogs
except ImportError:
    pass


def setupLogger(settings):
    if settings.logfile is not None:
        fmt = "%(asctime)s [%(levelname)s] %(message)s"
        date_fmt = "%Y-%m-%d %H:%M"

        try:
            consoleFormatter = coloredlogs.ColoredFormatter(fmt, date_fmt)
        except NameError:
            consoleFormatter = logging.Formatter(fmt, date_fmt)
        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(settings.loglevel_stderr)
        consoleHandler.setFormatter(consoleFormatter)

        fileFormatter = logging.Formatter(fmt, date_fmt)
        fileHandler = logging.FileHandler(settings.logfile)
        fileHandler.setLevel(settings.loglevel_file)
        fileHandler.setFormatter(fileFormatter)

        logging.getLogger().setLevel(0)
        logging.getLogger().addHandler(fileHandler)
        logging.getLogger().addHandler(consoleHandler)
    else:
        try:
            coloredlogs.install(
                fmt=fmt, datefmt=date_fmt, level=settings.loglevel_stderr
            )
        except NameError:
            logging.basicConfig(
                format=fmt, datefmt=date_fmt, level=settings.loglevel_stderr
            )
