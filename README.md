# schelp-watch

Watches SuperCollider HelpSource, and rebuilds changed files whenever they are changed.

The intended workflow is to freely edit HelpSources, and just reload a browser tab to see changes.

## Dependencies
- Python 3
- [watchdog](https://github.com/gorakhargosh/watchdog/) `$ pip install watchdog`

## Usage
Watch your HelpSource and open (-o) SC Help in a browser:
```
$ ./schelp-watch /full/path/to/HelpSource -o
```
Watch your build folder: will use correct sclang, SCClassLibrary and HelpSource from a supercollider source code repository. Remember to use the build folder and not the source directory's root.
```
$ ./schelp-watch --build ~/.local/src/supercollider/build -o
```

Full usage:
```
$ ./schelp-watch -h
usage: schelp-watch [-h] [--build] [--sclang sclangCommand] [--config sclangConfig] [-o] helpSourceDir [helptargetDir]

Watch SuperCollider HelpSource directory, and rebuild Help files on source changes.

positional arguments:
  helpSourceDir         HelpSource directory to watch for changes, or build directory if using --build
  helptargetDir         Optional: where to save compiled HelpFiles

optional arguments:
  -h, --help            show this help message and exit
  --build               Optional: use a supercollider build directory instead of an HelpSource directory. Will find sclang, config and HelpSource
                        from there (useful to work on sc main codebase).
  --sclang sclangCommand
                        Optional: sclang command (default: sclang)
  --config sclangConfig
                        Optional: sclang config file
  -o                    Optional: open SC Help (using .openOS in sclang)
```

## How it works
schelp-watch runs a sclang process (with default config), to rebuild Help files whenever their source changes.

## Known issues
- Completely untested on mac and windows. Most certainly requires more work for those platforms.
- The most "secure" way to use this tool is to make sure it's running an sclang instance that was compiled together with SCClassLibrary and HelpSource in use. This ensures sclang will be able to compile the class library, and SCDoc will be able to find all methods that are defined in the HelpSource. Errors can happen when, for instance, using an older version of sclang with the SCClassLibrary and/or HelpSource from git's develop branch. This is why this tool's `--build` option was introduced.
