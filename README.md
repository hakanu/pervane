![](https://github.com/hakanu/pervane/wiki/general_look.png)

# Pervane | [Demo](https://youtu.be/2WiFvcgV6lo) | [Install & Run](https://github.com/hakanu/pervane/wiki/Install-&-Run-instructions) | [Wiki](https://github.com/hakanu/pervane/wiki) | [Discuss](https://reddit.com/r/pervane/)

[![](https://img.shields.io/badge/status-stable-green.svg)](https://pypi.org/pypi/pervane/)
![](https://img.shields.io/badge/dynamic/json?color=green&label=downloads&query=data%5B0%5D.downloads&url=https%3A%2F%2Fpypistats.org%2Fapi%2Fpackages%2Fpervane%2Foverall)
[![](https://img.shields.io/pypi/v/pervane.svg)](https://pypi.org/pypi/pervane/)
[![](https://img.shields.io/pypi/pyversions/pervane.svg)](https://pypi.org/pypi/pervane/)
[![](https://img.shields.io/pypi/l/pervane.svg)](https://pypi.org/pypi/pervane/)

Pervane is a plain text file based note taking and knowledge base building tool.
It doubles as simple file server to render given directories files in web
browser while it can be used as a cloud IDE too with awesome code highlighting.
It's like python's built-in SimpleHTTPServer but a little bit feature richer
like WYSIWYG note taking experience, sidebar with infinite number of nesting,
blazing fast text search, file moving, creating from the browser etc.

Main use case is to create, edit, serve and search the markdown notes in
combination with example source files.

If you are using plain text based note taking, this can be helpful for adhoc
mediums like operating systems which don't have large desktop app ecosystem like
ChromeOS or mobile OS like Android and iOS.

## Features

* Completely private, your files, your computer, no database, no installation
  (apart from some general python packages). There is no statistic collection through any medium. (I only check [pypi stats](https://pypistats.org/packages/pervane))
* Self hosted (working on a managed version if anyone is interested, drop a messsage!)
* Notes are stored as plain text files with the names given by yourself. Pervane
  doesn't rename automatically.
* Extremely fast UI with quick note switches.
* Tabbed UI.
* No added metadata files etc. Just globs your files, caches for N seconds and
  creates the file tree.
* Source of truth is your own file system so you can use your favorite markdown
  editor to modify your notes: QOwnNotes, VSCode, Sublime Text etc.
* Ignore some files in order not to be shown on the sidebar.
* Flask based server, totally hackable, just modify, it's all yours.
* Minimal dependencies, single binary.
* Uses [silver searcher (ag)](https://github.com/ggreer/the_silver_searcher) for
  searching in an instant throughout the whole folder.
* Thanks to ag, no indexing or prework is done for search. You can just start
  using Pervane with one line command.
* File tree with proper infinite number of nesting, works well for hierarchical
  note taking and knowledge base building.
* Cookie based authentication.
* No stats collection, all private.
* Rich text editing experience thanks to [editor.md](https://pandao.github.io/editor.md/).
* Spell checker
* Find an replace within the editor.
* Hide/show preview
* Full screen editing mode with F11 or toolbar
* Hide/show toolbar
* Lots of themes thanks to editor.md
* Move files in between directories with drag & drop functionality.
* Keyboard shortcuts
* Quick fuzzy file name search
* Edit code notes directly
* Drag & Drop file upload in anywhere in the page
* Image/Video rendering in case you they are in the directory.
* Directory browser with breadcrumb paths.
* TeX/KaTeX, emoji, task list support.
* WYSIWYG editor
* Toggle-able sidebar.
* Dark mode by default with many themes like monokai, solarized etc.
* Side-by-side markdown preview with sync scroll.
* Full screen Zen mode for writing.
* Autosave.

## [Screenshots](https://github.com/hakanu/pervane/wiki/Screenshots-Gallery)

![Generel view of the app](https://github.com/hakanu/pervane/wiki/flow_chart.png)

All of the screenshots and more video are located in [Pervane Wiki](https://github.com/hakanu/pervane/wiki).

## Install via pip

```shell
screen
pip install pervane

# First make sure you create the admin user
pervane --mode=init

# Then run the app for reals.
# You can login with your recently created credentials.
pervane --dir=example/
```

When you go to localhost:5000, Pervane only accepts 1
user. So your notes will only be visible by this single user.

⚠️ If you see a server error, delete your cookies and retry.

### If you are upgrading from a version before 0.0.9

You will probably see errors about user is not existing. You need to run `pervane --mode=init` first.
I've changed user auth mode again (had to, because flask-user is deprecated). Sorry about it.

Package details here: https://pypi.org/project/pervane/

You can run Pervane also with Docker or build it from source. Please visit
[Pervane Wiki](https://github.com/hakanu/pervane/wiki/Install-&-Run-instructions)
for more installation options.

## Contribute

Please and thank you :)

```shell
# Init:
git clone https://github.com/hakanu/pervane.git && cd pervane

# Set up local env.
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt

# Run
python3 pervane/serve.py --debug=true
```
