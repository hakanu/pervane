# Pervane

Pervane is a bare minimum plain text file based note taking and knowledge base building tool.
It doubles as simple file server to render server files in web browser.
It's like python's built-in SimpleHTTPServer but a little bit feature richer like WYSIWYG note taking experience, infinite number of nesting, blazing fast text search etc.
Main use case is to edit, serve and search the markdown notes in combination with example source files.

If you are using plain text based note taking, this can be helpful for adhoc mediums like operating systems which don't have large desktop app ecosystem like ChromeOS or mobile OS like Android and iOS.

Personally tried many alternatives like [allmark](https://github.com/andreaskoch/allmark), [mdserv](https://www.npmjs.com/package/markserv), [markdown-server](https://pypi.org/project/markdown-server/) but none of them seem like providing all features I'm looking for. I just want to be able to see the folder hierarchy and fuzzy text search and some better-than-basic markdown rendering.

## Features

* Completely private, your files, your computer, no database, no installation (apart from some general python packages).
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

* Fetch the single python script to somewhere in your machine.
* Run it in screen or tmux.

```shell
# Run it in screen to make it always run.
screen

# Download the latest version.
wget -O -N - https://raw.githubusercontent.com/hakanu/pervane/master/init.sh | bash
```

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

~~* Fix repetitions in the file tree~~
~~* Simple expand/collapse logic in file tree.~~
* Files with spaces sometimes cause filenotfound
~~* mermaid.js integration~~ (Comes for free with TUI editor)
~~* Mindmap and flowchart rendering support.~~ (Comes for free with TUI editor)

~~* Edit the files?~~

