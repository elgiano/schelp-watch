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
Full usage:
```
$ ./schelp-watch -h
usage: schelp-watch [-h] [-o] helpSourceDir [helptargetDir]

Watch SuperCollider HelpSource directory, and rebuild Help files on
source changes.

positional arguments:
  helpSourceDir  HelpSource directory to watch for changes
  helptargetDir  Optional: where to save compiled HelpFiles

optional arguments:
  -h, --help     show this help message and exit
  -o             Optional: open SC Help (using .openOS in sclang)
```

## How it works
schelp-watch runs a sclang process (with default config), to rebuild Help files whenever their source changes.
