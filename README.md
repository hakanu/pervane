![](https://github.com/hakanu/pervane/raw/master/docs/pervane_logo_small.png)

# Pervane | [Demo](https://www.youtube.com/watch?v=sUr_qzeBxHI)

[![](https://img.shields.io/badge/status-stable-green.svg)](https://pypi.org/pypi/pervane/)
![](https://img.shields.io/badge/dynamic/json?color=green&label=downloads&query=data%5B0%5D.downloads&url=https%3A%2F%2Fpypistats.org%2Fapi%2Fpackages%2Fpervane%2Foverall)
[![](https://img.shields.io/pypi/v/pervane.svg)](https://pypi.org/pypi/pervane/)
[![](https://img.shields.io/pypi/pyversions/pervane.svg)](https://pypi.org/pypi/pervane/)
[![](https://img.shields.io/pypi/l/pervane.svg)](https://pypi.org/pypi/pervane/)

Pervane is a bare minimum plain text file based note taking and knowledge base building tool.
It doubles as simple file server to render given directories files in web browser.
It's like python's built-in SimpleHTTPServer but a little bit feature richer like WYSIWYG note taking experience, sidebar with infinite number of nesting, blazing fast text search, file moving, creating from the browser etc.

Main use case is to create, edit, serve and search the markdown notes in combination with example source files.

If you are using plain text based note taking, this can be helpful for adhoc mediums like operating systems which don't have large desktop app ecosystem like ChromeOS or mobile OS like Android and iOS.

Personally tried many alternatives as file server like [allmark](https://github.com/andreaskoch/allmark), [mdserv](https://www.npmjs.com/package/markserv), [markdown-server](https://pypi.org/project/markdown-server/) but none of them seem like providing all features I'm looking for. I just want to be able to see the folder hierarchy and fuzzy text search and some better-than-basic markdown rendering.

For the other note taking and knowledge base building apps, there is always something missing although how advanced they go.

What I need:

* Privacy, my notes are my eyes only.
* Be able take notes from multiple entry points: desktop, web, phone, tablet.
* Quickly search notes in any medium.
* Hold my whole knowledge accumulated over the course of the years (around 4k notes).
* Easy export so it doesn't lock me in.
* Easy import so I can onboard without any problems.
* Be able to self host
* Nice markdown editor
* Respect my folder hierarchy
* Don't mess with my file names
* git-able so that I can maintain the versions.
* Hackable with standard CLI tools (ag, rsync, scp, tar, git etc)
* Be able to show source code files not only markdown.
* Take code notes, create a code snippet repository and be able to find them back easily.

## Comparison

Inspired from this one from notable author.

![](https://notable.md/static/images/comparison.png)

* Google Keep: Always my choice on mobile. Need a long term place for my things.
  * Can not do markdown - only bullet lists.
  * Can not do inline images.
  * Really hard to export.
  * Note limit is not that big.
* Notion.so: Want to love it but...
  * Impossible to bulk import multiple files.
  * Copy/paste is a hussle. It has its own blocking system which makes it hard
  to copy all and paste somewhere else.
  * Not free.
* Trello: Kanban approach is great,
  * not so good for knowledgebase building.
  * Search is weird, hard to make it one shot.
* Notable: Good for desktop use, no mobile option.
  * I can not control file names. It has its own convention for folders (folder != notebook).
  * Source is closed.
  * Could be used as a markdown editor.
  * Bulk import is hard to use.
* Trilium: My all time favorite.
  * Based on a database which causes lots of conflicts to me in each upgrade.
  * Web UI is not so good in mobile browsers especially on iPad.
* Evernote
  * Hierarchy level is limited.
  * Overall free sync size is also limited.
* Onenote: Old favorite
  * Hierarchy is limited
  * Hard to bulk import
  * Hard to bulk export
* Joplin
  * Renames the files in its own way.
  * Hard to integrate with any other system.
* Boostnote: Another old favorite
  * Uses files but uses cjson format which is not actually markdown.
  * Not under active development
* QOwnNotes: Nice but meh
  * Doesn't give much joy while using.
* Vnote: Perfect for desktop use.
  * No web option
  * Creates \_vnote.json files.
  * Creates index for search.
* NextCloud with carnet and NC notes
  * Extremely slow.
  * Not so pleasent in mobile.
* VSCode: I can hear you are saying I do the same thing with any file editor.
  * Well, you need a platform which supports that editor.
* Cloud coding editors like [coder-server](https://github.com/cdr/code-server)
  * Too CPU intensive in the client side due to heavy js logic.
* Standard notes: Checks most of my boxes. They exist in all platforms, awesome stuff.
  * Not file based. Backup location txt files with their own format and name.
  * No bulk import/export. So I could have never onboarded fully onto this.
* Zim: Similar to pervane, file based.
  * Desktop app only. 
  * No web browser, platform dependent. Can not edit notes from ipad since
  there is no client. Need to sync files and then use an editor.
* dokuwiki: Personal wiki builder with tons of extensions. Solid option with files.
  * Wiki syntax (not my favorite), but you can install markdown extension apparently.
  * (Personal opinion) I have hard time to manage php servers. 

Please shoot an email if I miss anything.

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
* Rich text editing experience thanks to [editor.md](https://pandao.github.io/editor.md/)
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
* Image rendering in case you they are in the directory.

### Keyboard shortcuts

* Ctrl + s : Save the file.
* Ctrl + p : Focus on quick search box on the left sidebar 

### Sync - backup

Since it's normal file system files, you can use any sync mechanism to sync your files with one of these
- [Syncthing](https://syncthing.net/): my go-to self hosted syncing mechanism, too few impact on CPU
- [Dropbox](https://www.dropbox.com/): Not my favorite since it's 3rd party, unpredictable load on host CPU and battery life of the mobile phone.
  - You can go with headless dropbox, similar to syncthing, not so bad.
- [Google Drive](https://drive.google.com): 3rd party. Their file stream is pretty cool, similar to headless dropbox. But no linux client yet :/
  - https://support.google.com/a/answer/7491144?hl=en
- [Microsoft OneDrive](): 3rd party. I was using for my onenote sync. They are pretty good actually.
- [Nextcloud](): Similar to dropbox but self hosted. I'm currently using this. 
- git: I use two way backup, regularly committing notes to a private git repo (bitbucket, gitlab etc) and also syncing with nextcloud.
  - I can have revisions and note versions for free by using this.
- insert_your_favorite_sync_tool

### Mobile

I'm working on a lightweight mobile app to list and modify the notes.
For now you can use an mobile editor app with a syncing app as a workaround.
I use syncthing for this. 

### Testimonials

I have moved all my keep notes, blog posts and project wiki notes from trello and notion.so to pervane.
They total around 324 directories, 1579 files
`tree -a .`

## But it's not

* A dropbox replacement
* Photo album generator
* FTP server
* Cloud code editor

### Demo 

#### Video

[![Pervane note taking app demo](http://img.youtube.com/vi/sUr_qzeBxHI/0.jpg)](https://www.youtube.com/watch?v=sUr_qzeBxHI)

#### Screenshots

![Generel view of the app](https://github.com/hakanu/pervane/raw/master/docs/screenshots/1.jpg)

![Table preview in markdown editor](https://github.com/hakanu/pervane/raw/master/docs/screenshots/2.jpg)

![tex and katex preview in the markdown editor](https://github.com/hakanu/pervane/raw/master/docs/screenshots/3.jpg)

![Flowcharts preview](https://github.com/hakanu/pervane/raw/master/docs/screenshots/4.jpg)

![Sequence diagram in the editor](https://github.com/hakanu/pervane/raw/master/docs/screenshots/5.jpg)

![Settings](https://github.com/hakanu/pervane/raw/master/docs/screenshots/6.jpg)

![Create new directory](https://github.com/hakanu/pervane/raw/master/docs/screenshots/7.jpg)

![Edit recently created file](https://github.com/hakanu/pervane/raw/master/docs/screenshots/8.jpg)

![Folder hierarchy in file browser](https://github.com/hakanu/pervane/raw/master/docs/screenshots/9.jpg)

![Editing this file from this app](https://github.com/hakanu/pervane/raw/master/docs/screenshots/10.jpg)

## Install

### Via pip

```shell
screen
pip install pervane
pervane --dir=example/
```
When you go to localhost:5000, you need to register.
Pervane only accepts 1 user. So your notes will only be visible by this single user.

Package details here: https://pypi.org/project/pervane/

### Without pip

* Fetch the single python script to somewhere in your machine.
* Run it in screen or tmux.

```shell
# Run it in screen to make it always run.
screen

# Download the latest version.
git clone https://github.com/hakanu/pervane.git
cd pervane/pervane
python3 serve.py --dir=example/
```

## Update

The tool is still under heavy development, I update the package in pypi multiple
times per week. Would be great if you keep updating with:

```
pip install --upgrade pervane
```

## Options

* `--dir`: Note root directory. File tree will be generated from this. If `PERVANE_HOME` environment variable is set and --dir is not provided, `PERVANE_HOME` is used.
* `--host`: defaults to 0.0.0.0. Hostname to be binded.
* `--port`: defaults to 5000. Port number to be binded.
* `--username`: DEPRECATED. Authentication is now based on cookie based login. defaults to 'hakuna'. Username for basic http auth.
* `--password`: DEPRECATED. Authentication is now based on cookie based login. defaults to 'matata'. Username for basic http auth.
* `--front_page_message`: / message.
* `--cache_seconds`: Seconds to bust the cache. Mainly used for file tree re-reading.
* `--debug`: Enable more verbose logging.
* `--version`: Show version.

## Contribute

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

## Stack

Tried to keep the code as simple as possible since I need to take notes today.

* Flask based python web server
* jquery, bootstrap, bootswatch, dropzone.js, editor.md.

## TODO

* ~~Fix repetitions in the file tree~~
* ~~Simple expand/collapse logic in file tree.~~
* ~~Files with spaces sometimes cause filenotfound~~
* ~~mermaid.js integration~~ (Comes for free with TUI editor)
* ~~Mindmap and flowchart rendering support.~~ (Comes for free with TUI editor)
* Maybe delete file/dir functionality? Maybe not - security reasons.
* ~~Edit the files?~~
* ~~Some editor view?~~
* ~~Keyboard shortcuts~~
* ~~Image uploads~~
* ~~Image previews in the folders~~
* Embeded pdf reader 

## Keep the engine running

https://www.buymeacoffee.com/haku