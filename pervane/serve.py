"""Simple plain text based note taking app to serve and files
with directory hierarchy.

# Dependencies:

- Flask as python server.
- Jinja2 for templating.
- Bootstrap
- A little jquery
- Actually no more, transitioned to editor.md
   https://pandao.github.io/editor.md
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
pip install flask markdown2 Flask-Caching Flask-HTTPAuth 

# Run simple:
python3 serve.py 

# Run flask way:
export FLASK_APP=serve.py; export FLASK_ENV=development; flask run 
"""
import argparse
import base64
import json
import logging
import mimetypes
import os
import re
import subprocess
import sys

from jinja2 import Environment, BaseLoader
from flask import Flask, render_template, request, jsonify, redirect
from flask_caching import Cache
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

mimetypes.init()

parser = argparse.ArgumentParser(description='Process input from user.')
parser.add_argument('--host', dest='host', default='0.0.0.0',
                    help='hostname to be binded')
parser.add_argument('--port', dest='port', default='5000',
                    help='port to be binded')
parser.add_argument('--dir', dest='root_dir', default='./',
                    help='Working folder to show the tree.')
parser.add_argument('--username', dest='username', default='hakuna',
                    help='Authentication username')
parser.add_argument('--password', dest='password', default='matata',
                    help='Authentication password')
parser.add_argument('--cache_seconds', dest='cache_seconds', default=2,
                    help='Cache the sidebar file tree creation.')
parser.add_argument(
    '--ignore_patterns', dest='ignore_patterns', nargs='*',
    default=["env/.*", ".git", ".*.swp", ".*.pyc", "__pycache__", ".allmark",
             "_vnote.json", "!!!meta.json", "PaxHeader", ".nojekyll",
             ".*.sqlite"],
    help='Ignored file patterns during file tree creation.')
parser.add_argument(
    '--front_page_message',
    dest='front_page_message',
    default='Welcome to Pervane! This is default welcome message.',
    help='Cache the sidebar file tree creation.')
args = parser.parse_args()
print('loaded args %s', args)

logging.basicConfig(level=logging.DEBUG)
cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__, template_folder='templates')
cache.init_app(app)
auth = HTTPBasicAuth()

users = {
    args.username: generate_password_hash(args.password),
}


# Add custom jinja filter.
def escapejs(val):
    # TODO(hakanu): Need to figure out \u escaping in the notes.
    # This sub modifies the original content. 
    return re.sub(r'`', '\`', re.sub(r'\\u', '\\a', val))


def _get_template(html):
    env = Environment(loader=BaseLoader, autoescape=True)
    env.filters['escapejs'] = escapejs
    return env.from_string(html)


def get_mime_type(path):
  return mimetypes.guess_type(path)[0]
      

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False


@cache.cached(timeout=args.cache_seconds, key_prefix='_make_tree')
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

            if check_match(fn):
               continue

            if os.path.isdir(fn):
                tree['children'].append(_make_tree(fn))
            else:
                tree['children'].append(dict(name=name, path=fn))
    return tree


def check_match(file_path):
  for pattern in args.ignore_patterns:
    result = re.search(pattern, str(file_path))
    if result:
      return True


@app.route('/')
@auth.login_required
def front_page_handler():
    return render_template(
        'index.html', tree=make_tree(args.root_dir),
        html_content=args.front_page_message)


@app.route('/file')
@auth.login_required
def file_handler():
    path = request.args.get('f', '')
    if not path:
        return 'No path is given'
    path = path.strip()
    if not path.startswith(args.root_dir):
        logging.info('no auth')
        return (
            'Not authorized to see this dir, must be under: ' +
            args.root_dir)
    path = path.strip()
    html_content = ''
    content = ''
    mime_type = get_mime_type(path)
    logging.info('mime_type: %s', mime_type)
    if (not mime_type.startswith('image/') and 
        not mime_type.startswith('video/') and
        not mime_type.startswith('text/')):
      return ('No idea how to show this file %s' % path)

    # Text is our main interest.
    if mime_type.startswith('text/'):
      try:
        with open(path, 'r') as f:
          content = f.read()
        html_content = content
      except Exception as e:
        logging.error('There is an error while reading: %s', str(e))
        return 'File reading failed with ' + str(e)
    elif mime_type.startswith('image/'):
      try:
        with open(path, 'rb') as f:
          content = base64.b64encode(f.read()).decode('ascii')
        html_content = content
      except Exception as e:
        logging.error('There is an error while reading: %s', str(e))
        return 'File reading failed with ' + str(e)

    _, ext = os.path.splitext(path)
    return render_template('index.html',
        path=path, html_content=html_content, md_content=content, ext=ext,
        tree=make_tree(args.root_dir), mime_type=mime_type)


@app.route('/api/get_content')
@auth.login_required
def api_get_content_handler():
    path = request.args.get('f', '')
    if not path.startswith(args.root_dir):
        logging.info('no auth')
        return 'Not authorized to see this dir, must be under: %s' % args.root_dir
    try:
        with open(path, 'r') as f:
          content = f.read()
        return jsonify({'result': 'success', 'content': content})
    except Exception as e:
        return jsonify({'result': 'smt went wrong ' + str(e)})


@app.route('/api/update', methods=['POST'])
@auth.login_required
def api_update_handler():
    updated_content = request.form.get('updated_content', '')
    file_path = request.form.get('file_path', '')
    if not file_path:
        return jsonify({'result': 'File path is empty'})
    
    if not file_path.startswith(args.root_dir):
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

    if not parent_path.startswith(args.root_dir):
        return jsonify({'result': 'Unauth file modification'})

    if new_node_name.endswith('/'):
        path = os.path.join(parent_path, new_node_name)
        logging.info('Creating new node as dir %s', path)
        try:
            os.mkdir(path)
        except OSError:
            return redirect('/?message=failed_to_creat_dir:' + path, code=302)
        else:
            return redirect('/?message=created_dir:' + path, code=302)
    else:
        suffix = '' if new_node_name.endswith('.md') else '.md'
        path = os.path.join(parent_path, new_node_name + suffix)
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
    cmd = ['ag', query, args.root_dir, '--ackmate', '--stats', '-m', '2']
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
    return render_template('index.html',
        search_results=results, query=query, stats=stats_str,
        tree=make_tree(args.root_dir))


def cli_main():
    """Used within the python package cli."""
    app.run(host=args.host, port=args.port)


if __name__ == '__main__':
    app.run(host=args.host, port=args.port)

