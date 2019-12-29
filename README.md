# Pervane

Simple file server to render files in browser.
It's like python's built-in SimpleHTTPServer but a little bit feature richer.
Main use case is for serving and searching the markdown notes in combination with example source files.

If you are using plain text based note taking, this can be helpful for adhoc mediums.

Personally tried many alternatives like [allmark](https://github.com/andreaskoch/allmark), [mdserv](https://www.npmjs.com/package/markserv), [markdown-server](https://pypi.org/project/markdown-server/) but none of them seem like providing all features I'm looking for. I just want to be able to see the folder hierarchy and fuzzy text search and some better-than-basic markdown rendering.

## Features

* Single python file.
* Flask based server, totally hackable.
* Minimal dependencies, single binary.
* Uses silver searcher (ag) for searching in an instant throughout the whole folder.
* File tree with proper nesting.
* Basic http authentication.

## Install

* Fetch the single python script to somewhere in your machine.

```shell
# Init:
virtualenv -p python3 env
source env/bin/activate
pip install flask
pip install markdown2
pip install Flask-Caching
pip install Flask-HTTPAuth

# Download the latest version.
wget https://raw.githubusercontent.com/hakanu/pervane/master/serve.py

# Run:
export FLASK_APP=serve.py;  flask run 
```

* Modify serve.py's configuration section to add your folder to be searched.

## TODO

* Files with spaces sometimes cause filenotfound
* mermaid.js integration
* Mindmap and flowchart rendering support.
* Edit the files?

