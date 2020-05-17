// TODO(hakanu): Get rid of this file contents and move
// vue logic here from the template.

Array.prototype.remove = function () {
  var what, a = arguments, L = a.length, ax;
  while (L && this.length) {
    what = a[--L];
    while ((ax = this.indexOf(what)) !== -1) {
      this.splice(ax, 1);
    }
  }
  return this;
};

function fuzzy(source, s) {
  var hay = source.toLowerCase(), i = 0, n = -1, l;
  s = s.toLowerCase();
  for (; l = s[i++];) if (!~(n = hay.indexOf(l, n + 1))) return false;
  return true;
};

// Get expand/collapse memory from localstorage.
for (var i = 0; i < localStorage.length; i++) {
  var key = localStorage.key(i);
  var value = localStorage.getItem(key);
  // Hacky but useful way to generate ids from folder paths.
  // needed to use false as a str because is(visible) is serialized :/
  if (value != 'false') {
    $('#' + key).eq(0).css("display", "block");
  }
}


// demo data
var treeData = {
  name: "My Tree",
  children: [
    { name: "hello" },
    { name: "wat" },
    {
      name: "child folder",
      children: [
        {
          name: "child folder",
          children: [{ name: "hello" }, { name: "wat" }]
        },
        { name: "hello" },
        { name: "wat" },
        {
          name: "child folder",
          children: [{ name: "hello" }, { name: "wat" }]
        }
      ]
    }
  ]
};

// define the tree-item component
Vue.component("tree-item", {
  template: "#item-template",
  props: {
    item: Object
  },
  data: function () {
    return {
      isOpen: false
    };
  },
  computed: {
    isFolder: function () {
      return this.item.children && this.item.children.length;
    }
  },
  methods: {
    toggle: function () {
      if (this.isFolder) {
        this.isOpen = !this.isOpen;
      }
    },
    makeFolder: function () {
      if (!this.isFolder) {
        this.$emit("make-folder", this.item);
        this.isOpen = true;
      }
    }
  }
});


var app = new Vue({
  el: '#app',
  delimiters: ['[[', ']]'],
  data: {
    message: 'Hello Vue!',
    rootDirPath: rootDirPath,
    searchOp: {
      query: searchQuery,
      results: searchResults,
      stats: searchStats,
    },
    treeData: treeData,
  },
  methods: {
    addNode: function (parent) {
      console.log('vue add node');
      $('#modal-input-parent-path').attr('value', parent);
      // Prevent root to be like //.
      if (parent != '/') {
        $('#modal-input-prefix').text(parent + '/');
      }
      $('#nodeModal').modal();
      setTimeout(function () {
        $('#modal-input-new-node-name').focus();
      }, 500);
    },
    makeFolder: function (item) {
      Vue.set(item, "children", []);
      this.addItem(item);
    },
    addItem: function (item) {
      item.children.push({
        name: "new stuff"
      });
    }
  },
})

function showShortcutsModal() {
  // Show the modal upon click.
  $('#shortcuts-modal').modal();
}

function showSettingsModal() {
  // Show the modal upon click.
  $('#settings-modal').modal();

  // Init settings.
  // Modal should be initialized for these.
  if (localStorage.settingsKatex) {
    $('#settings-katex')[0].checked = localStorage.settingsKatex == '1';
  }

  if (localStorage.settingsTaskLists) {
    $('#settings-task-lists')[0].checked = localStorage.settingsTaskLists == '1';
  }

  if (localStorage.settingsCharts) {
    $('#settings-charts')[0].checked = localStorage.settingsCharts == '1';
  }

  if (localStorage.settingsSequences) {
    $('#settings-sequences')[0].checked = localStorage.settingsSequences == '1';
  }

  if (localStorage.settingsCodeFolding) {
    $('#settings-code-folding')[0].checked = localStorage.settingsCodeFolding == '1';
  }

  if (localStorage.settingsEmoji) {
    $('#settings-emoji')[0].checked = localStorage.settingsEmoji == '1';
  }

  if (localStorage.settingsToolbar) {
    $('#settings-toolbar')[0].checked = localStorage.settingsToolbar == '1';
  }
}

$('.expand').click(function () {
  var nearest_ul = $('ul', $(this).parent()).eq(0);
  nearest_ul.toggle();
  window.localStorage.setItem(nearest_ul.attr('id'),
    nearest_ul.is(':visible'));
});

// Path may come from the GET so init it.
if (pathToInitEditor) {
  console.log('initing the editor');
  initEditor(pathToInitEditor);
} else {
  console.log('no need to init the editor');
}

// Try to restore previously open tabs.
var openTabPaths = localStorage.openTabPaths ? localStorage.openTabPaths.split(',') : [];
var activeTabPath = localStorage.activeTabPath ? localStorage.activeTabPath : null
restoreTabs();

var editor = null;

function initEditor(path) {
  console.log('Initing the editor for path: ', path);
  // Add a div for editor to be created into.
  if (!$('#editor')[0]) {
    $('#div-editor').eq(0).append('<div id="editor"><textarea></textarea></div>');
  }
  if (path) {
    $.get(
      "/api/get_content", {
      f: path
    },
      function (data) {
        console.log('Got result', data.result);
        if (data.result == 'success') {
          // TODO(hakanu): No idea why this is not working.
          // editor.setValue(data.content);
          // editor.setMarkdown(data.content);
          editor = editormd("editor", {
            width: "100%",
            height: "150%",
            taskList: (localStorage.settingsTaskLists) ? (localStorage.settingsTaskLists == '1') : false,
            // autoHeight: true,
            codeFold: (localStorage.settingsCodeFolding) ? (localStorage.settingsCodeFolding == '1') : false,
            searchReplace: true,
            flowChart: (localStorage.settingsCharts) ? (localStorage.settingsCharts == '1') : false,
            sequenceDiagram: (localStorage.settingsSequences) ? (localStorage.settingsSequences == '1') : false,
            tex: (localStorage.settingsKatex) ? (localStorage.settingsKatex == '1') : false,
            emoji: (localStorage.settingsEmoji) ? (localStorage.settingsEmoji == '1') : false,
            toolbar: (localStorage.settingsToolbar) ? (localStorage.settingsToolbar == '1') : true,
            theme: (localStorage.theme) ? localStorage.theme : "dark",
            previewTheme: (localStorage.previewTheme) ? localStorage.previewTheme : "dark",
            editorTheme: (localStorage.editorTheme) ? localStorage.editorTheme : "pastel-on-dark",
            // TODO(hakanu): Needed to load like this. Otherwise editor
            // puts its own placeholder to the textarea instead of empty.
            markdown: data.content + '\n',
            path: "/static/js/lib/",  // Autoload modules mode.
            onload: function () {
              console.log('onload', this);
              // Make the preview pane non-default.
              // this.unwatch();
            }
          });
        } else {
          console.log('something went wrong while fetching the file content', data.result);
          $('#status').text('something went wrong while fetching the file content', data.result);
        }
      });
  }
}

function update() {
  var text = editor.getMarkdown();
  var file_path = $('#a-path').text();

  $.post(
    '/api/update', {
    updated_content: text,
    file_path: file_path
  }, function (result) {
    if (result.result == 'success') {
      $('#status').text('Updated @ ' + (new Date()));
    } else {
      $('#status').text('Failed to update @ ' + (new Date()));
    }
  });
}

function addNode(parent) {
}

function themeSelect(id, themes, lsKey, callback) {
  var select = $("#" + id);
  for (var i = 0, len = themes.length; i < len; i++) {
    var theme = themes[i];
    var selected = (localStorage[lsKey] == theme) ? " selected=\"selected\"" : "";
    select.append("<option value=\"" + theme + "\"" + selected + ">" + theme + "</option>");
  }

  select.bind("change", function () {
    var theme = $(this).val();
    if (theme === "") {
      alert("theme == \"\"");
      return false;
    }
    localStorage[lsKey] = theme;
    callback(select, theme);
  });
  return select;
}

themeSelect("editormd-theme-select", editormd.themes, "theme", function ($this, theme) {
  editor.setTheme(theme);
});

themeSelect("editor-area-theme-select", editormd.editorThemes, "editorTheme", function ($this, theme) {
  editor.setCodeMirrorTheme(theme);
});

themeSelect("preview-area-theme-select", editormd.previewThemes, "previewTheme", function ($this, theme) {
  editor.setPreviewTheme(theme);
});

$('#settings-katex').change(function () {
  if (this.checked) {
    localStorage.setItem('settingsKatex', 1);
  } else {
    localStorage.setItem('settingsKatex', 0);
  }
});

$('#settings-charts').change(function () {
  if (this.checked) {
    localStorage.setItem('settingsCharts', 1);
  } else {
    localStorage.setItem('settingsCharts', 0);
  }
});

$('#settings-task-lists').change(function () {
  if (this.checked) {
    localStorage.setItem('settingsTaskLists', 1);
  } else {
    localStorage.setItem('settingsTaskLists', 0);
  }
});

$('#settings-sequences').change(function () {
  if (this.checked) {
    localStorage.setItem('settingsSequences', 1);
  } else {
    localStorage.setItem('settingsSequences', 0);
  }
});

$('#settings-code-folding').change(function () {
  if (this.checked) {
    localStorage.setItem('settingsCodeFolding', 1);
  } else {
    localStorage.setItem('settingsCodeFolding', 0);
  }
});

$('#settings-emoji').change(function () {
  if (this.checked) {
    localStorage.setItem('settingsEmoji', 1);
  } else {
    localStorage.setItem('settingsEmoji', 0);
  }
});

$('#settings-toolbar').change(function () {
  if (this.checked) {
    localStorage.setItem('settingsToolbar', 1);
  } else {
    localStorage.setItem('settingsToolbar', 0);
  }
});

Dropzone.autoDiscover = false;

$(function () {
  var myDropzone = new Dropzone(document.body, {
    clickable: '.fileinput-button',
    url: '/upload',
    acceptedFiles: 'image/*,application/pdf',
    maxFilesize: 2,  // MB
  });

  myDropzone.on('addedfile', function (file) {
    console.log('File added');
  });

  myDropzone.on('success', function (file, response) {
    if (response.result == 'success') {
      window.location.replace('/file?f=' + response.entity);
    } else {
      $('#message').text('Fail:/ ' + response.message);
      myDropzone.removeFile(file);
    }
  });
});

// Fuzzy search.

$('#list-sidebar').hide();
$('#search-field').on('keyup', function () {
  var searchString = $(this).val();
  if (searchString == '') {
    $('#list-sidebar').hide();
  } else {
    $('#list-sidebar').children().remove();
    for (var i = 0; i < values.length; i++) {
      var path = values[i].path;
      if (fuzzy(path, searchString)) {
        $('#list-sidebar').append('<li><a href="/file?f=' + path + '">' + values[i].name + '</a></li>');
      }
    }
    $('#list-sidebar').show();
  }
});

// Ctrl + s saving.
$(document).keydown(function (event) {
  // 19 for Mac Command+S
  if (!(String.fromCharCode(event.which).toLowerCase() == 's' && event.ctrlKey) && !(event.which == 19)) return true;
  event.preventDefault();
  update();
  return false;
});

// Ctrl + p focus on quick search, sublime text style.
$(document).keydown(function (event) {
  // 19 for Mac Command+S
  if (!(String.fromCharCode(event.which).toLowerCase() == 'p' && event.ctrlKey) && !(event.which == 19)) return true;
  event.preventDefault();
  $('#search-field').focus();
  return false;
});

// Ctrl + i create new note in the first level directory.
$(document).keydown(function (event) {
  // 19 for Mac Command+S
  if (!(String.fromCharCode(event.which).toLowerCase() == 'i' && event.ctrlKey) && !(event.which == 19)) return true;
  event.preventDefault();
  addNode('/');
  return false;
});

// Drag drop file move
function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  ev.dataTransfer.setData('source_path', ev.target.id);
}

function drop(ev) {
  ev.preventDefault();
  var source_path = ev.dataTransfer.getData('source_path');
  var dest_dir = ev.target.id;

  $.get(
    '/api/move_file', {
    source_path: source_path,
    dest_dir: dest_dir,
  }, function (result) {
    if (result.result == 'success') {
      console.log('Moved the file, refreshing');
      window.location.replace('/');
    } else {
      console.log('Failed to move the file');
    }
  });
}

// File/directory creation form handling.
$('#form-add-node').submit(function (event) {
  event.preventDefault();
  console.log('adding node');
  var parentPath = $('#modal-input-parent-path').val();
  var newNodeName = $('#modal-input-new-node-name').val();
  $.post(
    '/api/add_node', {
    parent_path: parentPath,
    new_node_name: newNodeName,
  }, function (result) {
    if (result.result == 'success') {
      console.log('Created file, refreshing');
      var dest = '/';
      if (!result.entity.endsWith('/')) {
        dest = '/file?f=' + result.entity;
      }
      window.location.replace(dest);
    } else {
      console.log('Failed to create the file or dir');
      $('#message').text(result.message);
    }
  });
});

// Autosave timeout, 2 seconds.
var timeoutId;
$('#editor').on('input propertychange', function () {
  console.log('Autosaving');

  // Runs 2s after the las/t change    
  clearTimeout(timeoutId);
  timeoutId = setTimeout(function () {
    update();
  }, 2000);
});

function handleTabSwitch(e) {
  const id = e.target.id;
  const path = id.replace('-tab-li', '').replace('-tab', '');
  console.log('Activating tab: ', id, 'with path:', path);
  activeTabPath = path;
  //  $(this).tab('show');
  if ($('#editor')) {
    $('#editor').remove();
  }
  $('#a-path').text(path);
  initEditor(path);
}

function saveOpenTabs() {
  localStorage.setItem('openTabPaths', openTabPaths.join(','));
}

function updateOpenTabs() {
  localStorage.setItem('openTabPaths', openTabPaths.join(','));
}

function handleTabClose(e) {
  const id = e.target.id;
  const path = id.replace('-tab-close', '');
  console.log('Closing tab: ', id, 'with path:', path);
  //$('#' + path + '-tab').tab('dispose');
  document.getElementById(path + '-tab-li').remove();
  openTabPaths.remove(path);
  console.log('after tab close: ', openTabPaths);
  saveOpenTabs();
}

function restoreTabs() {
  console.log('Restoring tabs for ', openTabPaths);
  for (var i = 0; i < openTabPaths.length; i++) {
    appendTab(openTabPaths[i]);
  }
  updateActiveTab();
}

function escapePathId(pathId) {
  return pathId.replace(/\//g, '\\/');
}

function updateActiveTab() {
  if (activeTabPath) {
    localStorage.setItem('activeTabPath', activeTabPath);
    console.log('activating the tab for ', activeTabPath);
    //$('#' + activeTabPath + '-tab-li').tab('show');
    console.log(document.getElementById(activeTabPath + '-tab-li'));
    //document.getElementById(activeTabPath + '-tab-li').click();//.tab('show');
    //var pathId = escapePathId(activeTabPath + '-tab-li');
    //console.log('element: ', pathId, $('#' + pathId).eq(0));
    //  Jquery selectors don't work with backslashes.
    //document.getElementById(activeTabPath + '-tab-li').style.color = '#00bc8c';
    document.getElementById(activeTabPath + '-tab-li').click();
  }
}

function appendTab(id) {
  $('#myTab').append(`
    <li class="nav-item nav-link" id="${id}-tab-li">
      <span>
        <span class="" id="${id}-tab" data-toggle="tab" href="#" role="tab" aria-controls="home" aria-selected="true">${id}</span>
      </span>
      &nbsp;&nbsp;
      <span>
        <a class="btn-tab-close" style="color:red;" href="#" id="${id}-tab-close">X</a>
      </span>
    </li>`);
}

function removeTab(id) {

}

// Load the file upon file click without refreshing the page.
$('.file-path').click(function (e) {
  e.preventDefault();
  if ($('#editor')) {
    $('#editor').remove();
  }
  $('#a-path').text(e.target.id);
  initEditor(e.target.id);
  const id = e.target.id;
  const path = e.target.id;

  if (!openTabPaths.includes(path)) {
    appendTab(id);
  }
  openTabPaths.push(path);
  updateOpenTabs();

  activeTabPath = path;
  updateActiveTab();

  // Listen new tab too.
  $('#myTab li').on('click', function (e) {
    e.preventDefault();
    handleTabSwitch(e);
  });

  // Listen tab close.
  $('#myTab .btn-tab-close').on('click', function (e) {
    e.preventDefault();
    console.log('closing tab: ', e.target.id);
    const path = e.target.id.replace('-tab-close', '');
    document.getElementById(path + '-tab-li').remove();
    openTabPaths.remove(path);
  });
});

// List to tab switch.
$('#myTab li').on('click', function (e) {
  e.preventDefault();
  if (e.target.id.includes('-close')) {
    1 < tab > onsole.log('closing this shouild nout handle that event');
  }
  handleTabSwitch(e);
  activeTabPath = e.target.id.replace('-tab-li', '').replace('-tab', '');
  updateActiveTab();
});

// Listen to tab close.
$('#myTab .btn-tab-close').on('click', function (e) {
  e.preventDefault();
  console.log('closing tab: ', e.target.id);
  const path = e.target.id;
  handleTabClose(e);
});