import configparser
import os
import sys
import urllib.request
from gettext import gettext as _

import utils


class Settings:
    sitename = None
    confdir = None
    url = None
    sitename = None
    threshold = 1
    cmp_threshold = 0.35
    title_scale = 2
    logfile = None
    loglevel_file = "INFO"
    loglevel_stderr = "CRITICAL"
    appendlvl = False
    outputfile = None
    feedfile = None

    # parse arguments and read feed from file/url
    def read_argv(self):
        if len(sys.argv) != 2:
            print(_("no file/url given"))
            sys.exit(-1)
        self.url = sys.argv[1]
        if self.url[0:4] == "http":
            self.feedfile = urllib.request.urlopen(self.url)
            self.sitename = self.url.split("/")[2]
        else:
            self.feedfile = self.url
            self.sitename = self.url.split(".")[0]

    def read_settings(self):
        # read env-variables
        self.confdir = os.getenv(
            "FEED_FILTER_CONF", os.path.join(os.getenv("HOME"), ".feedfilter")
        )
        debug_mode = os.getenv("DEBUG", "False")

        # read configfile
        configs = configparser.ConfigParser()
        configs.read(os.path.join(self.confdir, "feedfilter.conf"))
        for section in configs:
            if section == "DEFAULT":
                config = configs[section]
            elif self.url.find(section) != -1:
                config = configs[section]
                self.sitename = config.get("sitename", self.sitename)
            else:
                continue
            self.threshold = float(config.get("threshold", self.threshold))
            self.cmp_threshold = float(config.get("cmp_threshold", self.cmp_threshold))
            self.title_scale = float(config.get("title_scale", self.title_scale))
            self.logfile = config.get("logfile", self.logfile)
            self.loglevel_file = config.get("loglevel", self.loglevel_file)
            self.loglevel_stderr = config.get("verboselevel", self.loglevel_stderr)
            self.appendlvl = utils.toBool(config.get("appendlvl", self.appendlvl))
            self.outputfile = config.get("outputfile", self.outputfile)
        if debug_mode == "dev":
            self.loglevel_file = "DEBUG"
            self.loglevel_stderr = "DEBUG"
            self.outputfile = "output.xml"
