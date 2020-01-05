![](docs/pervane_logo_small.png)

# Pervane

Pervane is a bare minimum plain text file based note taking and knowledge base building tool.
It doubles as simple file server to render server files in web browser.
It's like python's built-in SimpleHTTPServer but a little bit feature richer like WYSIWYG note taking experience, infinite number of nesting, blazing fast text search etc.
Main use case is to edit, serve and search the markdown notes in combination with example source files.

If you are using plain text based note taking, this can be helpful for adhoc mediums like operating systems which don't have large desktop app ecosystem like ChromeOS or mobile OS like Android and iOS.

Personally tried many alternatives like [allmark](https://github.com/andreaskoch/allmark), [mdserv](https://www.npmjs.com/package/markserv), [markdown-server](https://pypi.org/project/markdown-server/) but none of them seem like providing all features I'm looking for. I just want to be able to see the folder hierarchy and fuzzy text search and some better-than-basic markdown rendering.

## [Discuss](https://reddit.com/r/pervane/)

## Features

* Completely private, your files, your computer, no database, no installation (apart from some general python packages).
* Self hosted (working on a managed version if anyone is interested, drop a messsage!)
* Notes are stored as plain text files with the names given by yourself. Pervane doesn't rename automatically.
* No added metadata files etc. Just globs your files, caches for N seconds and creates the file tree.
* Source of truth is your own file system so you can use your favorite markdown editor to modify your notes: QOwnNotes, VSCode, Sublime Text etc. 
* Ignore some files in order not to be shown on the sidebar.
* Single python file.
* Flask based server, totally hackable, just modify, it's all yours.
* Minimal dependencies, single binary.
* Uses [silver searcher (ag)](https://github.com/ggreer/the_silver_searcher) for searching in an instant throughout the whole folder.
* Thanks to ag, no indexing or prework is done for search. You can just start using Pervane with one line command.
* File tree with proper infinite number of nesting, works well for hierarchical note taking and knowledge base building.
* Basic http authentication.
* No stats collection, all private.
* Rich text editing experience thanks to [TUI Editor](https://github.com/nhn/tui.editor)

## Install

### Via pip

```shell
screen
pip install pervane
pervane --dir=/tmp/my_notes
```

Package details here: https://pypi.org/project/pervane/

### Without pip

* Fetch the single python script to somewhere in your machine.
* Run it in screen or tmux.

```shell
# Run it in screen to make it always run.
screen

# Download the latest version.
wget -O -N - https://raw.githubusercontent.com/hakanu/pervane/master/init.sh | bash
```

## Options

* `--dir`: Note root directory. File tree will be generated from this.
* `--host`: defaults to 0.0.0.0. Hostname to be binded.
* `--port`: defaults to 5000. Port number to be binded.
* `--username`: defaults to 'hakuna'. Username for basic http auth.
* `--password`: defaults to 'matata'. Username for basic http auth.
* `--front_page_message`: / message.
* `--cache_seconds`: Seconds to bust the cache. Mainly used for file tree re-reading.

## Contribute

```shell
# Init:
git clone https://github.com/hakanu/pervane.git

# Set up local env.
virtualenv -p python3 env
source env/bin/activate
pip install flask markdown2 Flask-Caching Flask-HTTPAuth

# Run
python3 serve.py

# Run alternative:
export FLASK_APP=serve.py ; flask run 
```

* Modify serve.py's configuration section to add your folder to be searched.

## TODO

* ~~Fix repetitions in the file tree~~
* ~~Simple expand/collapse logic in file tree.~~
* Files with spaces sometimes cause filenotfound
* ~~mermaid.js integration~~ (Comes for free with TUI editor)
* ~~Mindmap and flowchart rendering support.~~ (Comes for free with TUI editor)
* Maybe delete file/dir functionality? Maybe not - security reasons.
* ~~Edit the files?~~
* ~~Some editor view?~~

## Keep the engine running

<style>.bmc-button img{width: 35px !important;margin-bottom: 1px !important;box-shadow: none !important;border: none !important;vertical-align: middle !important;}.bmc-button{padding: 7px 10px 7px 10px !important;line-height: 35px !important;height:51px !important;min-width:217px !important;text-decoration: none !important;display:inline-flex !important;color:#FFFFFF !important;background-color:#FF813F !important;border-radius: 5px !important;border: 1px solid transparent !important;padding: 7px 10px 7px 10px !important;font-size: 22px !important;letter-spacing: 0.6px !important;box-shadow: 0px 1px 2px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;margin: 0 auto !important;font-family:'Cookie', cursive !important;-webkit-box-sizing: border-box !important;box-sizing: border-box !important;-o-transition: 0.3s all linear !important;-webkit-transition: 0.3s all linear !important;-moz-transition: 0.3s all linear !important;-ms-transition: 0.3s all linear !important;transition: 0.3s all linear !important;}.bmc-button:hover, .bmc-button:active, .bmc-button:focus {-webkit-box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;text-decoration: none !important;box-shadow: 0px 1px 2px 2px rgba(190, 190, 190, 0.5) !important;opacity: 0.85 !important;color:#FFFFFF !important;}</style><link href="https://fonts.googleapis.com/css?family=Cookie" rel="stylesheet"><a class="bmc-button" target="_blank" href="https://www.buymeacoffee.com/haku"><img src="https://cdn.buymeacoffee.com/buttons/bmc-new-btn-logo.svg" alt="Buy me a coffee"><span style="margin-left:15px;font-size:28px !important;">Buy me a coffee</span></a>

