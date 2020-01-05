"""Simple server to serve  files with directory hierarchy.

# Dependencies:

- Flask as python server.
- Jinja2 for templating.
- Bootstrap
- A little jquery
- TUI editor for markdown editing.
- highlight.js for simple code highlighting for non-md files.

Discuss: https://reddit.com/r/pervane 
Contribute: https://github.com/hakanu/pervane

Jinja2 template is embedded into python code.
Although this is not the best option, in order to provide
single file app, this was necessary.

All dependencies in the template is imported from CDNs. So
should be fairly fast and cached.

# Init:
virtualenv -p python3 env
source env/bin/activate
pip install flask markdown2 Flask-Caching Flask-HTTPAuth mistune

# Run simple:
python3 serve.py 

# Run flask way:
export FLASK_APP=serve.py; export FLASK_ENV=development; flask run 
"""
import json
import logging
import os
import re
import subprocess
import sys

from jinja2 import Environment, BaseLoader
from flask import Flask, render_template, request, jsonify, redirect
from flask_caching import Cache
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.DEBUG)
cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__)
cache.init_app(app)
auth = HTTPBasicAuth()


_CONFIG = {}
try:
    _CONFIG = json.loads(open('config.json', 'r').read())
except Exception as e:
    logging.info('config.json can not be found, rename config_example.json to config.json for inspiration. Err: ', e)
logging.info('loaded config: %s', _CONFIG)
users = {
    _CONFIG['username']: generate_password_hash(_CONFIG['password']),
}

_INDEX_TEMPLATE = """
<html>
 <head>
    <title>Pervane - Plain text based note taking app</title>
    <link rel="stylesheet" href="//cdn.jsdelivr.net/gh/highlightjs/cdn-release@9.17.1/build/styles/default.min.css">
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" rel="stylesheet" >
    <link rel="stylesheet" href="https://uicdn.toast.com/tui-editor/latest/tui-editor.css"></link>
    <link rel="stylesheet" href="https://uicdn.toast.com/tui-editor/latest/tui-editor-contents.css"></link>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.48.4/codemirror.css"></link>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.12.0/styles/github.min.css"></link>
    <link href="https://fonts.googleapis.com/css?family=PT+Sans&display=swap" rel="stylesheet">
    <style>
      body {
        margin: 10px;
	font-family: 'PT Sans', sans-serif;
	/*        font-size: 1.5vw;*/
      }

      ul {
        padding-left: 10px;
      }

      ul li ul {
        display: none;
        padding-left: 10px;
      }
    </style>
 </head>
 <body>
    <div class="">
	<div class="row">
	    <div class="col-md-10">
		<div class="">
		  <form action="/search" method="GET">
		      <input type="text" class="form-control" name="query" placeholder="Search files with ag" aria-label="query" aria-describedby="basic-addon1">
		  </form>
		</div>
	    </div>
	    <div class="col-md-2">
                <p><a href="https://github.com/hakanu/pervane" target="_blank">About</a></p>
	    </div>
	</div>

        <div class="row">
            <div class="col-md-2">
		<p><a href="/">{{ tree.name }}</a></p>
		<ul>
		{%- for item in tree.children recursive %}
		    <li>
			{% if '.' in item.name and not item.name.startswith('.')  %}
			    <a href="/file?f={{ item.path }}">+{{ item.name }}</a>
			{% else %}
                            <a href="#" data-href="/dir?d={{ item.path }}" class="expand">/{{ item.name }}</a>&nbsp;&nbsp;
			    <span>
                              <a href="#" onclick="addNode('{{ item.path }}')">⊕</a>
                            </span>
			{% endif %}

			{%- if item.children -%}
			    <ul>{{ loop(item.children) }}</ul>
			{%- endif %}
		    </li>
		{%- endfor %}
		</ul>
            </div>

            <div class="col-md-10">
                {% if not search_results %}
		    <h6>
                        <a id="a-path" href="file://{{path}}" target="_blank">{{ path }}</a>&nbsp;&nbsp;
                        <span><a href="#" onclick="update()">💾</a></span>
                        <sub id="status"></sub>
                    </h6>
		    {% if ext == '.md' %}
                        {% if not md_content and html_content %}
                            <div>{{ html_content|safe }}</div>
                        {% else %}
                            <div id="editorSection"></div>
                        {% endif %}
		    {% else %}
			<pre><code class="{{ext|replace('.', '')}}">{{ html_content|e }}</code></pre>
		    {% endif %}
                {% else %}
                    <h6>Results for <b>{{ query|e }}</b></h6>
                    <p><sub>{{ stats }}</sub></p>
                    {% for result in search_results %}
		       <a href="/file?f={{ result.file}}" target="_blank">{{ result.file }}</a>
                       <ul>
                          {% for match in result.matches %}
			      <li><pre>{{match.snippet}}</pre></li>
                          {% endfor %}
                       </ul>
                    {% endfor %}
		{% endif %}
            </div>
        </div>
    </div>

    <!-- Modal -->
    <div class="modal fade" id="nodeModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered" role="document">
	<div class="modal-content">
	  <div class="modal-header">
	    <h5 class="modal-title" id="exampleModalLongTitle">Create new node</h5>
	    <button type="button" class="close" data-dismiss="modal" aria-label="Close">
	      <span aria-hidden="true">&times;</span>
	    </button>
	  </div>
          <form action="/api/add_node" method="POST">
	      <div class="modal-body">
		<p>Put / at the end if you want to create a directory. Otherwise we append a .md suffix for you.</p>
		<div class="input-group mb-3">
		    <input id="modal-input-parent-path" type="hidden" name="parent_path" class="form-control"> 
		    <div class="input-group-prepend">
		        <span id="modal-input-prefix" class="input-group-text"></span>
		    </div>
		    <input type="text" name="new_node_name" class="form-control" placeholder="Type new node's name">
		  </div>
	        </div>
	      <div class="modal-footer">
		<button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
		<button type="submit" class="btn btn-primary">Add node</button>
	      </div>
          </form>
	</div>
      </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.bundle.min.js"></script>
    <script src="//cdn.jsdelivr.net/gh/highlightjs/cdn-release@9.17.1/build/highlight.min.js"></script>
    <script src="https://uicdn.toast.com/tui-editor/latest/tui-editor-Editor-full.js"></script>
<!--    <script src="https://cdnjs.cloudflare.com/ajax/libs/Darkmode.js/1.5.4/darkmode-js.min.js"></script>-->
    <script>
    document.addEventListener('DOMContentLoaded', (event) => {
      document.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightBlock(block);
      });
    }); 

    // Consider enabling dark mode. Need more work though.
    // TUI Editor doesn't have dark mode.
    //new Darkmode().showWidget();

    $('.expand').click(function() {
      $('ul', $(this).parent()).eq(0).toggle();
    });

    {% if md_content and path %}
        console.log('initing the editor for path');
        initEditor('{{path}}');      
    {% endif %}

    var editor = new tui.Editor({
        el: document.querySelector('#editorSection'),
        previewStyle: 'tab',  // vertical|horizontal
        height: '900px',
	usageStatistics: false,
        initialEditType: 'markdown',
        {% if md_content %}
//	    initialValue: `{{ "md_content"|escapejs|safe }}`,
        {% else %}
	    initialValue: '', 
        {% endif %}
	exts: [
          {
            name: 'chart',
            minWidth: 100,
            maxWidth: 600,
            minHeight: 100,
            maxHeight: 300
          },
          'scrollSync',
          'colorSyntax',
          'uml',
          'mark',
          'table'
        ]
    });

    function initEditor(path) {
	$.get( 
	 "/api/get_content", { 
	     f: path 
	 }, 
	 function(data) { 
             if (data.result == 'success') {
	        editor.setValue(data.content);
	     } else {
                console.log('something went wrong while fetching the file content', data.result);
            	$('#status').text('something went wrong while fetching the file content', data.result);
             }
	 }); 
    }

    function update() {
       var text = editor.getMarkdown();
       var file_path = $('#a-path').text();
       $.post('/api/update', {updated_content: text, file_path: file_path}, function(result){
          console.log('Finished request', result, result.result);
          if (result.result == 'success') {
            $('#status').text('Updated @ ' + (new Date()));
            console.log('Reloading');
            location.reload();
          } else {
            $('#status').text('Failed to update @ ' + (new Date()));
	  }
       });
    }

    function addNode(parent) {
        console.log('adding node to parent', parent);
        $('#modal-input-parent-path').attr('value', parent);
        $('#modal-input-prefix').text(parent + '/');
        $('#nodeModal').modal();
    }
    </script>
 </body>
</html>
"""


# Add custom jinja filter.
def escapejs(val):
    # TODO(hakanu): Need to figure out \u escaping in the notes.
    # This sub modifies the original content. 
    return re.sub(r'`', '\`', re.sub(r'\\u', '\\a', val))


def _get_template():
    env = Environment(loader=BaseLoader, autoescape=True)
    env.filters['escapejs'] = escapejs
    return env.from_string(_INDEX_TEMPLATE)
      

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


@cache.cached(timeout=_CONFIG['cache_seconds'], key_prefix='_make_tree')
def make_tree(path):
    """Higher level function to be used with cache."""
    return _make_tree(path)


def _make_tree(path):
    """Recursive function to get the file/dir tree.

    Can not be cached due to recursion.
    """
    tree = dict(name=os.path.basename(path), path=path, children=[])

    if check_match(path):
       return 
    try:
        lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(_make_tree(fn))
            else:
                tree['children'].append(dict(name=name, path=fn))
    return tree


def check_match(file_path):
  for pattern in _CONFIG['ignore_patterns']:
    result = re.search(pattern, str(file_path))
    if result:
      return True


@app.route('/')
@auth.login_required
def front_page_handler():
    rtemplate = _get_template()
    return rtemplate.render(html_content=_CONFIG['front_page_message'], 
                            tree=make_tree(_CONFIG['root_dir']))


@app.route('/file')
@auth.login_required
def file_handler():
    path = request.args.get('f', '')
    if not path:
        return 'No path is given'
    path = path.strip()
    if not path.startswith(_CONFIG['root_dir']):
        logging.info('no auth')
        return 'Not authorized to see this dir, must be under: ' + _CONFIG['root_dir']
    path = path.strip()
    try:
        with open(path, 'r') as f:
            content = f.read()
    except Exception as e:
        logging.error('There is an error while reading: %s', str(e))
        return 'File reading failed with ' + str(e)
    html_content = 'root_dir'
    _, ext = os.path.splitext(path)
    rtemplate = _get_template()
    html_content = content
    return rtemplate.render(
        path=path, html_content=html_content, md_content=content, ext=ext,
        tree=make_tree(_CONFIG['root_dir'])) 


@app.route('/api/get_content')
@auth.login_required
def api_get_content_handler():
    path = request.args.get('f', '')
    if not path.startswith(_CONFIG['root_dir']):
        logging.info('no auth')
        return 'Not authorized to see this dir, must be under: ' + _CONFIG['root_dir']
    try:
        with open(path, 'r') as f:
            content = f.read()
        return jsonify({'result': 'success', 'content': content})
    except Exception as e:
        return jsonify({'result': 'smt went wrong ' + e})


@app.route('/api/update', methods=['POST'])
@auth.login_required
def api_update_handler():
    updated_content = request.form.get('updated_content', '')
    file_path = request.form.get('file_path', '')
    if not file_path:
        return jsonify({'result': 'File path is empty'})
    
    if not file_path.startswith(_CONFIG['root_dir']):
        return jsonify({'result': 'Unauth file modification'})

    if not updated_content:
        return jsonify({'result': 'File content is empty'})
    try:
        with open(file_path, 'w') as f:
            f.write(updated_content)
    except Exception as e:
        return jsonify({'result': 'update failed'})
    return jsonify({'result': 'success'}) 


@app.route('/api/add_node', methods=['POST'])
@auth.login_required
def add_node_handler():
    parent_path = request.form.get('parent_path', '')
    new_node_name = request.form.get('new_node_name', '')
    if not parent_path or not new_node_name:
         return redirect('/?message=path_can_not_be_empty', code=302)
    new_node_name = new_node_name.strip()

    if not parent_path.startswith(_CONFIG['root_dir']):
        return jsonify({'result': 'Unauth file modification'})

    if new_node_name.endswith('/'):
        path = os.path.join(_CONFIG['root_dir'], parent_path, new_node_name)
        logging.info('Creating new node as dir %s', path)
        try:
            os.mkdir(path)
        except OSError:
            return redirect('/?message=failed_to_creat_dir:' + path, code=302)
        else:
            return redirect('/?message=created_dir:' + path, code=302)
    else:
        suffix = '' if new_node_name.endswith('.md') else '.md'
        path = os.path.join(_CONFIG['root_dir'], parent_path, new_node_name + suffix)
        try:
            f = open(path, 'x')
        except OSError:
            return redirect('/?message=failed_to_creat_md:' + path, code=302)
        else:
            return redirect('/file?f=' + path, code=302)


@app.route('/search')
@auth.login_required
def search_handler():
    query = request.args.get('query', '')
    if not query:
        return 'You need to search for something'
    # ackmate mode for easier parsing.
    cmd = ['ag', query, _CONFIG['root_dir'], '--ackmate', '--stats', '-m', '2']
    logging.info('Running cmd: %s', cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()
    # Convert output from binary to string.
    output = output.decode('utf-8')
    lines = output.split('\n')
    results = []
    in_file_results = []
    fn = ''
    file_finished = False

    # Extract stats tail first.
    stats_str = ' '.join(lines[-6:])
    in_file_started = False
    for line in lines[:-6]:
       if line.startswith(':'):
           fn = line
           in_file_results = []
           file_finished = False
           in_file_started = True
           continue
       elif in_file_started and ';' in line:
           in_file_results.append({
                'snippet': line,
           })

       results.append({
	  'file': fn.replace(':', ''),
	  'matches': in_file_results,
       }) 

    html_body = ''
    rtemplate = _get_template()
    return rtemplate.render(
        search_results=results, query=query, stats=stats_str,
        tree=make_tree(_CONFIG['root_dir']))


if __name__ == '__main__':
    app.run(host=_CONFIG['host'], port=_CONFIG['port'])

