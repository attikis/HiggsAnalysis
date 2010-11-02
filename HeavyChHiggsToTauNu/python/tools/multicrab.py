import ConfigParser
import OrderedDict

def getTaskDirectories(opts, filename="multicrab.cfg"):
    if hasattr(opts, "dirs") and len(opts.dirs) > 0:
        return opts.dirs
    else:
        mc_ignore = ["MULTICRAB", "COMMON"]
        mc_parser = ConfigParser.ConfigParser(dict_type=OrderedDict.OrderedDict)
        mc_parser.read("multicrab.cfg")

        sections = mc_parser.sections()

        for i in mc_ignore:
            sections.remove(i)

#        sections.sort()

        return sections


def addOptions(parser):
    parser.add_option("--dir", "-d", dest="dirs", type="string", action="append", default=[],
                      help="CRAB task directory to have the files to merge (default: read multicrab.cfg and use the sections in it)")


def checkCrabInPath():
    try:
        retcode = subprocess.call(["crab"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError, e:
        if e.errno == errno.ENOENT:
            raise Exception("crab executable not found in $PATH. Is the crab environment loaded?")
        else:
            raise e
