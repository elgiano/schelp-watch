import sys
from os.path import relpath, abspath, join, dirname, splitext, exists
from os import getcwd, walk
import subprocess
import logging
from time import sleep
from argparse import ArgumentParser
from watchfiles import watch, Change


class ScLang:

    def __init__(self, sclangCommand="sclang", sclangConfig=None):
        self.__sclang = None
        self.executable = sclangCommand
        self.config = sclangConfig
        self.showingHelpBrowser = False

    def start(self, hide_sc_output=False):
        if self.running():
            return

        sclangArgs = [self.executable, "-i", "schelp-watch"]
        if self.config:
            sclangArgs += ["-al", self.config]

        out = subprocess.PIPE if hide_sc_output else None
        self.__sclang = subprocess.Popen(
            sclangArgs,
            bufsize=0,
            stdin=subprocess.PIPE,
            stdout=out,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            close_fds=True)
        self.stdout = self.__sclang.stdout
        self.stdin = self.__sclang.stdin

    def stop(self):
        if self.running():
            self.stdin.close()
            self.__sclang.wait()
            self.__sclang = None

    def running(self):
        return (self.__sclang is not None) and (self.__sclang.poll() is None)

    def evaluate(self, code, silent=False):
        code = code + ("\x1b" if silent else "\x0c")
        self.stdin.write(code)
        self.stdin.flush()

    def initSCDoc(self, helpSourceDir, helpTargetDir, extension):
        self.helpSourceDir = helpSourceDir
        # for extensions: add include path
        if extension:
            self.evaluate(f"LanguageConfig.addIncludePath(\"{helpSourceDir}\")")
        else:
            self.evaluate(f'SCDoc.helpSourceDir = "{helpSourceDir}"')

        if helpTargetDir:
            self.evaluate(f'SCDoc.helpTargetDir = "{helpTargetDir}"')
        else:
            self.makeTemporaryHelpTarget()

        self.evaluate("SCDoc.indexAllDocuments(false)")

    def makeTemporaryHelpTarget(self):
        self.evaluate('''
var target = PathName.tmp +/+ "schelp-watch";
if (File.exists(target)) { File.deleteAll(target) };
File.copy(SCDoc.helpTargetDir, target);
SCDoc.helpTargetDir = target;
"SCDoc temporary target: %".format(SCDoc.helpTargetDir)
          ''')

    def recompileScHelp(self, path):
        path = relpath(path, self.helpSourceDir)
        logging.info("reloading %s", path)

        sccode = f'''
var entry = SCDoc.parseFileMetaData("{self.helpSourceDir}","{path}");
if (entry.notNil) {{
    SCDoc.parseAndRender(entry);
    {'HelpBrowser.goTo(entry.destPath)' if self.showingHelpBrowser else ''}
}} {{
    warn("{path}: entry not found")
}}
        '''
        self.evaluate(sccode)

    def openHelp(self):
        self.showingHelpBrowser = True
        self.evaluate("HelpBrowser.instance")


def detectBuildMode(path):
    '''
    check if path looks like we are working at the supercollider git repo
    '''
    for p in [
        join(path, "lang", "sclang"),
        join(path, "build_sclang.cfg"),
        join(path, "..", "HelpSource")
    ]:
        if not exists(p):
            return False
    return True


def has_schelp_files(path):
    for root, _, files in walk(path):
        for f in files:
            if f.endswith(".schelp"):
                print(f"found some at {root}")
                return True
    return False


def parse_arguments():
    parser = ArgumentParser(description='''
Watches .schelp files, rebuilding and previewing Help files on source changes.
It can be used in build mode (for editing help files in SuperCollider's main repo), or extension mode (for Quarks and Extensions help files). If no mode is provided, schelp-watch will try to detect it automatically.
    ''')

    arg_group_mode = parser.add_mutually_exclusive_group()
    arg_group_mode.add_argument('--build', '-b', dest="mode", action="store_const", const="build",
                                help='specify "build mode": will find sclang, config and HelpSource from PATH (useful to work on sc main codebase). Use it when editing help files in sc main repo')
    arg_group_mode.add_argument('--extension', '-e', dest="mode", action="store_const", const="extension",
                                help='specify "extension mode": adds PATH to SuperCollider default HelpSource paths. Use it when editing Quarks and Extensions.')

    parser.add_argument('path', metavar="PATH", type=str, nargs="?", default=getcwd(),
                        help="in build mode: build folder; in extension mode: extension folder (default: current directory)")

    parser.add_argument('--target', metavar="helpTarget", type=str,
                        help='Optional: where to save compiled HelpFiles (default: make a temporary folder)')
    parser.add_argument('--sclang', metavar="sclangCommand", type=str, default="sclang",
                        help='Optional: sclang command (default: sclang)')
    parser.add_argument('--config', metavar="sclangConfig", type=str,
                        help='Optional: sclang config file')
    parser.add_argument('--quiet', '-q', action="store_true",
                        help='hide sclang output')
    parser.add_argument('--no-preview', '-n', action="store_true",
                        help='write to target, but don\'t open HelpBrowser')

    return parser.parse_args()


def main():

    logging.addLevelName(logging.WARNING, f"\033[1;33m{logging.getLevelName(logging.WARNING)}\033[1;0m")
    logging.addLevelName(logging.INFO, f"\033[1;34m{logging.getLevelName(logging.INFO)}\033[1;0m")
    logging.addLevelName(logging.ERROR, f"\033[1;31m{logging.getLevelName(logging.ERROR)}\033[1;0m")
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s] %(levelname)s %(message)s',
                        datefmt='%H:%M:%S')

    args = parse_arguments()
    srcDir = abspath(args.path)

    mode = args.mode
    # autodetect build mode for srcDir or srcDir/build
    if mode is None:
        build = detectBuildMode(srcDir)
        if not build and detectBuildMode(join(srcDir, "build")):
            build = True
            srcDir = join(srcDir, "build")
        mode = 'build' if build else 'extension'
    logging.info(f"Starting in {mode} mode at '{srcDir}'")

    if mode == "build":
        helpSourceDir = join(srcDir, "..", "HelpSource")
        sclangCommand = join(srcDir, "lang", "sclang")
        sclangConfig = join(srcDir, "build_sclang.cfg")
    else:
        logging.info("looking for schelp files...")
        if not has_schelp_files(srcDir):
            logging.error(f"couldn't find any .schelp file in {srcDir}")
            exit(1)
        helpSourceDir = srcDir
        sclangCommand = args.sclang
        sclangConfig = args.config

    helpTargetDir = abspath(args.target) if args.target else None
    logging.info(f"HelpSource: {helpSourceDir}");

    if sclangConfig is not None:
        logging.info(f"sclang config: {sclangConfig}")
    logging.info("Starting sclang ({})".format(sclangCommand));
    sclang = ScLang(sclangCommand, sclangConfig)
    sclang.start(args.quiet)

    logging.info("Initializing SCDoc");
    sclang.initSCDoc(helpSourceDir, helpTargetDir, mode == 'extension')
    if not args.quiet:
        logging.info("Opening SC Help");
        sclang.openHelp()

    def schelp_filter(change, path):
        return path.endswith(".schelp") and change != Change.deleted

    for changes in watch(helpSourceDir,
                         watch_filter=schelp_filter,
                         recursive=True, raise_interrupt=False):
        print(changes)
        paths = set(p for _, p in changes)
        for p in paths:
            sclang.recompileScHelp(p)


if __name__ == "__main__":
    main()
