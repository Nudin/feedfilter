import configparser
import os
import sys
import urllib.request

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

    def __init__(self):
        # read env-variables
        self.confdir = os.getenv(
            "FEED_FILTER_CONF", os.path.join(os.getenv("HOME"), ".feedfilter")
        )
        self.debug_mode = utils.toBool(os.getenv("DEBUG", "false"))
        self.configs = configparser.ConfigParser()
        self.configs.read(os.path.join(self.confdir, "feedfilter.conf"))

    # parse arguments and read feed from file/url
    def read_argv(self):
        arg = sys.argv[1]
        if arg[0:4] == "http":
            self.url = arg
            self.sitename = self.url.split("/")[2]
            config = self._search_config(self.url)
        elif arg in self.configs:
            try:
                self.url = self.configs[arg]["url"]
            except KeyError:
                print("Config does not specify an url")
                sys.exit(-1)
            self.sitename = arg
            config = self.configs[arg]
        else:
            self.url = "file://" + os.path.abspath(os.path.expanduser(arg))
            self.sitename = os.path.splitext(os.path.basename(arg))[0]
            config = self._search_config(self.url)
        self.feedfile = urllib.request.urlopen(self.url)
        if config:
            self._load_settings(config)

    def _search_config(self, term):
        for title, section in self.configs.items():
            if title in term:
                return section
        return None

    def _load_settings(self, config):
        self.sitename = config.get("sitename", self.sitename)
        self.threshold = config.getfloat("threshold", self.threshold)
        self.cmp_threshold = config.getfloat("cmp_threshold", self.cmp_threshold)
        self.title_scale = config.getfloat("title_scale", self.title_scale)
        self.logfile = config.get("logfile", self.logfile)
        self.loglevel_file = config.get("loglevel", self.loglevel_file)
        self.loglevel_stderr = config.get("verboselevel", self.loglevel_stderr)
        self.appendlvl = config.getboolean("appendlvl", self.appendlvl)
        self.outputfile = config.get("outputfile", self.outputfile)
        if self.debug_mode:
            self.loglevel_file = "DEBUG"
            self.loglevel_stderr = "DEBUG"
            self.outputfile = "output.xml"
