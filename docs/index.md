![](https://github.com/hakanu/pervane/raw/master/docs/pervane_logo_small.png)

# Pervane | [Demo](https://youtu.be/2WiFvcgV6lo) | [Install & Run](https://github.com/hakanu/pervane/wiki/Install-&-Run-instructions) | [Wiki](https://github.com/hakanu/pervane/wiki) | [Discuss](https://reddit.com/r/pervane/)

[![](https://img.shields.io/badge/status-stable-green.svg)](https://pypi.org/pypi/pervane/)
![](https://img.shields.io/badge/dynamic/json?color=green&label=downloads&query=data%5B0%5D.downloads&url=https%3A%2F%2Fpypistats.org%2Fapi%2Fpackages%2Fpervane%2Foverall)
[![](https://img.shields.io/pypi/v/pervane.svg)](https://pypi.org/pypi/pervane/)
[![](https://img.shields.io/pypi/pyversions/pervane.svg)](https://pypi.org/pypi/pervane/)
[![](https://img.shields.io/pypi/l/pervane.svg)](https://pypi.org/pypi/pervane/)

Pervane is a plain text file based note taking and knowledge base building tool.
It doubles as simple file server to render given directories files in web browser while it can be used as a cloud IDE too with awesome code highlighting.
It's like python's built-in SimpleHTTPServer but a little bit feature richer like WYSIWYG note taking experience, sidebar with infinite number of nesting, blazing fast text search, file moving, creating from the browser etc.

Main use case is to create, edit, serve and search the markdown notes in combination with example source files.

If you are using plain text based note taking, this can be helpful for adhoc mediums like operating systems which don't have large desktop app ecosystem like ChromeOS or mobile OS like Android and iOS.

Personally tried many alternatives as file server like [allmark](https://github.com/andreaskoch/allmark), [mdserv](https://www.npmjs.com/package/markserv), [markdown-server](https://pypi.org/project/markdown-server/) but none of them seem like providing all features I'm looking for. I just want to be able to see the folder hierarchy and fuzzy text search and some better-than-basic markdown rendering.

For the other note taking and knowledge base building apps, there is always something missing although how advanced they go.

## Features

* Completely private, your files, your computer, no database, no installation (apart from some general python packages).
* Self hosted (working on a managed version if anyone is interested, drop a messsage!)
* Notes are stored as plain text files with the names given by yourself. Pervane doesn't rename automatically.
* Extremely fast UI with quick note switches.
* Tabbed UI.
* No added metadata files etc. Just globs your files, caches for N seconds and creates the file tree.
* Source of truth is your own file system so you can use your favorite markdown editor to modify your notes: QOwnNotes, VSCode, Sublime Text etc.
* Ignore some files in order not to be shown on the sidebar.
* Flask based server, totally hackable, just modify, it's all yours.
* Minimal dependencies, single binary.
* Uses [silver searcher (ag)](https://github.com/ggreer/the_silver_searcher) for searching in an instant throughout the whole folder.
* Thanks to ag, no indexing or prework is done for search. You can just start using Pervane with one line command.
* File tree with proper infinite number of nesting, works well for hierarchical note taking and knowledge base building.
* Cookie based authentication.
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
* Image/Video rendering in case you they are in the directory.
* Directory browser with breadcrumb paths.
* TeX/KaTeX, emoji, task list support.
* WYSIWYG editor
* Toggle-able sidebar.
* Dark mode by default with many themes like monokai, solarized etc.
* Side-by-side markdown preview with sync scroll.
* Full screen Zen mode for writing.
* Autosave.

## Install via pip

```shell
screen
pip install pervane
pervane --dir=example/
```

When you go to localhost:5000, you need to register.
Pervane only accepts 1 user. So your notes will only be visible by this single user.

⚠️ If you see a server error, delete your cookies and retry.

Package details here: https://pypi.org/project/pervane/

You can run pervane also with Docker, or build it from source. Please visit
[Pervane
wiki](https://github.com/hakanu/pervane/wiki/Install-&-Run-instructions) for
more installation and run options.

### Demo

#### [Video](https://youtu.be/2WiFvcgV6lo)

[![Pervane note taking app demo](http://img.youtube.com/vi/2WiFvcgV6lo/0.jpg)](https://youtu.be/2WiFvcgV6lo)

#### Screenshots

All of the screenshots and more video are located in [Pervane Wiki](https://github.com/hakanu/pervane/wiki) but here are some:

* General look and feel with advanced markdown editor and tabbed view and sidebar for file tree.

![Generel view of the app](https://github.com/hakanu/pervane/wiki/markdown.jpg)

* File tree on the sidebar with infinite nestability and same as your favorite file browser's hierarchy.

![](https://github.com/hakanu/pervane/wiki/tabs.jpg)

![tex and katex preview in the markdown editor](https://github.com/hakanu/pervane/wiki/tex_katex_support.jpg)

* Flow Charts within markdown

![Flowcharts preview](https://github.com/hakanu/pervane/wiki/flow_chart.jpg)

* GFM task lists in markdown

![](https://github.com/hakanu/pervane/wiki/gfm_task_lists.jpg)

* Cloud IDE (code editor in your browser)

![](https://github.com/hakanu/pervane/wiki/code_editor_search_replace.jpg)

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
  * Copy/paste is a hussle. It has its own blocking system which makes it hard to copy all and paste somewhere else.
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
  * No web browser, platform dependent. Can not edit notes from ipad since there is no client. Need to sync files and then use an editor.
* dokuwiki: Personal wiki builder with tons of extensions. Solid option with files.
  * Wiki syntax (not my favorite), but you can install markdown extension apparently.
  * (Personal opinion) I have hard time to manage php servers.

Please shoot an email if I miss anything.

## Sync - backup

Since pervane works with files, you can sync your files with your favorite sync
tool. Please visit [Pervane
Wiki](https://github.com/hakanu/pervane/wiki/Sync-&-Backup) for more
information.

### Testimonials

I have moved all my keep notes, blog posts and project wiki notes from trello and notion.so to pervane.
They total around 324 directories, 1579 files
`tree -a .`

## But it is not a...

* Dropbox replacement
* Photo album generator
* FTP server

## Migration paths

* [Move from Google Keep to Pervane](https://github.com/hakanu/pervane/wiki/Move-Keep-Notes-to-Pervane)
* [WIP] Move from Evernote to Pervane
* [WIP] Move from Onenote to Pervane

## Why did you build yet another markdown editor?

Fair question, what I need was:

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

And there was no good alternative, so here is pervane for you.

## Contribute

Pervane is an open-source project. The development happens on
[Github](https://github.com/hakanu/pervane). Feel free to chime in!

## Stack

Tried to keep the code as simple as possible since I need to take notes today.

* Flask based python web server
* Vue.js, jquery, bootstrap, bootswatch, dropzone.js, editor.md.

## Keep the engine running

https://www.buymeacoffee.com/haku
