import configparser
import os
import utils


def read_settings(url):
    global sitename
    global logfile, loglevel_file, loglevel_stderr, appendlvl
    global confdir, outputfile
    global cmp_threshold, threshold, title_scale
    # read env-variables
    confdir = os.getenv('FEED_FILTER_CONF',
                        os.path.join(os.getenv('HOME'), ".feedfilter"))
    debug_mode = os.getenv('DEBUG',  "False")

    # read configfile
    configs = configparser.ConfigParser()
    configs.read(os.path.join(confdir, 'feedfilter.conf'))
    # default settings
    threshold = 1
    cmp_threshold = 0.35
    title_scale = 2
    logfile = None
    loglevel_file = 'INFO'
    loglevel_stderr = 'CRITICAL'
    appendlvl = False
    outputfile = None
    if url[0:4] == "http":
        sitename = url.split('/')[2]
    else:
        sitename = url.split('.')[0]
    for section in configs:
        if section == 'DEFAULT':
            config = configs[section]
        elif url.find(section) != -1:
            config = configs[section]
            sitename = config.get('sitename', sitename)
        else:
            continue
        threshold = float(config.get('threshold', threshold))
        cmp_threshold = float(config.get('cmp_threshold', cmp_threshold))
        title_scale = float(config.get('title_scale', title_scale))
        logfile = config.get('logfile', logfile)
        loglevel_file = config.get('loglevel', loglevel_file)
        loglevel_stderr = config.get('verboselevel', loglevel_stderr)
        appendlvl = utils.toBool(config.get('appendlvl', appendlvl))
        outputfile = config.get('outputfile', outputfile)
    if debug_mode == "dev":
        loglevel_file = 'DEBUG'
        loglevel_stderr = 'DEBUG'
        outputfile = 'output.xml'
