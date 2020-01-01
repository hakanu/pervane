"""Simple server to serve  files with directory hierarchy.

# Init:
virtualenv -p python3 env
source env/bin/activate
pip install flask markdown2 Flask-Caching Flask-HTTPAuth

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
# Python3 way of globbing patterns.
from pathlib import Path

import markdown2
from jinja2 import Environment, BaseLoader
from flask import Flask, render_template, request
from flask_caching import Cache
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__)
cache.init_app(app)
auth = HTTPBasicAuth()


_CONFIG = {}
try:
    _CONFIG = json.loads(open('config.json', 'r').read())
except Exception as e:
    logging.info('config.json can not be found, rename config_example.json to config.json for inspiration. Err: ', e)
logging.info('loaded config: ', _CONFIG)
users = {
    _CONFIG['username']: generate_password_hash(_CONFIG['password']),
}

_INDEX_TEMPLATE = """
<html>
 <head>
    <link rel="stylesheet" href="//cdn.jsdelivr.net/gh/highlightjs/cdn-release@9.17.1/build/styles/default.min.css">
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" rel="stylesheet" >
    <style>
      body {
        margin: 10px;
      }

      ul li ul {
        display: none;
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
            <div class="col-md-4">
		<p><a href="/">{{ tree.name }}</a></p>
		<ul>
		{%- for item in tree.children recursive %}
		    <li>
			{% if '.' in item.name  %}
			    <a href="/file?f={{ item.path }}">{{ item.name }}</a>
			{% else %}
			    <a href="#" data-href="/dir?d={{ item.path }}" class="expand">/{{ item.name }}</a>
			{% endif %}

			{%- if item.children -%}
			    <ul>{{ loop(item.children) }}</ul>
			{%- endif %}
		    </li>
		{%- endfor %}
		</ul>
            </div>

            <div class="col-md-8">
                {% if html_content %}
		    <h6><a href="file://{{path}}" target="_blank">{{ path }}</a></h6>
		    {% if ext == '.md' %}
			<div>{{ html_content|safe }}</div>
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

    <script src="https://code.jquery.com/jquery-3.4.1.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.bundle.min.js"></script>
    <script src="//cdn.jsdelivr.net/gh/highlightjs/cdn-release@9.17.1/build/highlight.min.js"></script>
    <script>
     document.addEventListener('DOMContentLoaded', (event) => {
	  document.querySelectorAll('pre code').forEach((block) => {
	    hljs.highlightBlock(block);
	  });
	}); 

    $('.expand').click(function() {
      $('ul', $(this).parent()).eq(0).toggle();
    });
    </script>
 </body>
</html>
"""


@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


@cache.cached(timeout=50, key_prefix='make_tree')
def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])

#    if check_match(path):
#       return 
    try:
        lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                tree['children'].append(dict(name=name, path=fn))
    return tree


def check_match(file_path):
  for pattern in _CONFIG['ignore_patterns']:
    result = re.search(pattern, str(file_path))
    if result:
      return True

        
def get_files(root_path):
    files = []
    for f in Path(root_path).rglob('*'):
        if not check_match(f):
            files.append({
	      'path': str(f),
              'name': os.path.basename(f),
              'is_dir': f.is_dir(),
            })
    return files


@app.route('/')
@auth.login_required
def front_page_handler():
    rtemplate = Environment(loader=BaseLoader).from_string(
        _INDEX_TEMPLATE)
    return rtemplate.render(html_content=_CONFIG['front_page_message'], 
                            tree=make_tree(_CONFIG['root_dir']))


@app.route('/file')
@auth.login_required
def file_handler():
    path = request.args.get('f', '')
    content = open(path, 'r').read()
    html_content = ''
    _, ext = os.path.splitext(path)
    rtemplate = Environment(loader=BaseLoader).from_string(
        _INDEX_TEMPLATE)
    if ext == '.md':
        html_content = markdown2.markdown(content)
    else:
        html_content = content
    return rtemplate.render(
        path=path, html_content=html_content, ext=ext,
        tree=make_tree(_CONFIG['root_dir'])) 


@app.route('/dir')
def dir_handler():
    path = request.args.get('d', '')
    return path


@app.route('/search')
@auth.login_required
def search_handler():
    query = request.args.get('query', '')
    if not query:
        return 'You need to search for something'
    # ackmate mode for easier parsing.
    cmd = ['ag', query, _CONFIG['root_dir'], '--ackmate', '--stats', '-m', '2']
    logging.info('Running cmd: ', cmd)
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
    rtemplate = Environment(loader=BaseLoader).from_string(
        _INDEX_TEMPLATE)
    return rtemplate.render(
        search_results=results, query=query, stats=stats_str,
        tree=make_tree(_CONFIG['root_dir'])) 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

