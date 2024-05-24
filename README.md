# schelp-watch
Live preview and autoreload for editing SuperCollider HelpFiles.

## Installation
```
pipx install schelp-watch
```

## How it works
schelp-watch runs a sclang process (with default config), to rebuild Help files whenever their source changes. It won't pollute your current HelpFiles cache, because by default it compiles to a temporary one.

The intended workflow is to freely edit HelpSources, and quickly see how they look in SuperCollider HelpBrowser. It can be used for editing SuperCollider main repo's HelpFiles, and as well for Extensions and Quarks.

## Usage
schelp-watch can be used with no arguments. Just cd to your Extension folder, or to your supercollider's main repo clone, and run:
```
schelp-watch
```
It will detect build or extension mode, watch your .schelp files, run SC HelpBrowser and autoreload.

### build mode
Use this for editing HelpSource in SuperCollider main repo:
- it needs to find a `build` folder, if not provided with one
- it will then use the `sclang` binary from that `build folder`, and also its `sclang_config` file.
- it will watch the `HelpSource` folder, one level above the `build` folder

If schelp-watch is run without specifying a mode, and those three conditions are met, it will start in "build mode" automatically. Otherwise it can be specified explicitly:
```
schelp -b BUILD_FOLDER
```

### extension mode
Use this for editing Quarks or Extension HelpFiles.
- start default sclang with default config
- add EXTENSION_FOLDER to sclang include paths (after compilation)
```
schelp -e EXTENSION_FOLDER 
```
schelp-watch will start in extension mode automatically if it can't start in build mode, and if it can find any .schelp file in any subdirectory of PATH.

## Full usage:
```
$ ./schelp-watch -h
usage: schelp-watch [-h] [--build | --extension] [--target helpTarget] [--sclang sclangCommand] [--config sclangConfig] [--quiet]
                    [--no-preview]
                    [PATH]

Watches .schelp files, rebuilding and previewing Help files on source changes. It can be used in build mode (for editing help files in
SuperCollider's main repo), or extension mode (for Quarks and Extensions help files). If no mode is provided, schelp-watch will try to
detect it automatically.

positional arguments:
  PATH                  in build mode: build folder; in extension mode: extension folder (default: current directory)

options:
  -h, --help            show this help message and exit
  --build, -b           specify "build mode": will find sclang, config and HelpSource from PATH (useful to work on sc main codebase). Use
                        it when editing help files in sc main repo
  --extension, -e       specify "extension mode": adds PATH to SuperCollider default HelpSource paths. Use it when editing Quarks and
                        Extensions.
  --target helpTarget   Optional: where to save compiled HelpFiles (default: make a temporary folder)
  --sclang sclangCommand
                        Optional: sclang command (default: sclang)
  --config sclangConfig
                        Optional: sclang config file
  --quiet, -q           hide sclang output
  --no-preview, -n      write to target, but don't open HelpBrowser
```

## Dependencies
- Python 3
- [watchfiles](https://github.com/samuelcolvin/watchfiles)

## Known issues
- Still completely untested on mac and windows. Most certainly requires more work for those platforms.
- The most "secure" way to use this tool is to make sure it's running an sclang instance that was compiled together with SCClassLibrary and HelpSource in use. This ensures sclang will be able to compile the class library, and SCDoc will be able to find all methods that are defined in the HelpSource. Errors can happen when, for instance, using an older version of sclang with the SCClassLibrary and/or HelpSource from git's develop branch. This is why this tool's `build mode` was introduced.
