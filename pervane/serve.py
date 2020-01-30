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
- dropzone.js for drag/drop uploads.

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
import datetime
import json
import logging
import mimetypes
import os
import re
import shutil
import subprocess
import sys

from jinja2 import Environment, BaseLoader
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_caching import Cache
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

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
    default=['env/.*', '.git', '.*.swp', '.*.pyc', '__pycache__', '.allmark',
             '_vnote.json', '!!!meta.json', 'PaxHeader', '.nojekyll',
             '.*.sqlite'],
    help='Ignored file patterns during file tree creation.')
parser.add_argument(
    '--note_extensions', dest='note_extensions', nargs='*',
    default=['.txt', '.md', '.markdown'],
    help='File patterns to be used for main note taking/editing functionality.')
parser.add_argument(
    '--front_page_message',
    dest='front_page_message',
    default='Welcome to Pervane! This is default welcome message.',
    help='Cache the sidebar file tree creation.')
args = parser.parse_args()
print('loaded args %s', args)

# We should always work with absolute path in order not to cause security issues
_ROOT_DIR = os.path.abspath(args.root_dir)

logging.basicConfig(level=logging.DEBUG)
cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__, template_folder='templates')
cache.init_app(app)
auth = HTTPBasicAuth()

users = {
    args.username: generate_password_hash(args.password),
}

UPLOAD_FOLDER = _ROOT_DIR  #'/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def program_installed(binary):
  rc = subprocess.call(['which', binary])
  if rc == 0:
    return True 
  else:
    return False


def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
  guessed_type = mimetypes.guess_type(path)
  if guessed_type[0]:
    return guessed_type[0]
  logging.error('Can not extact the mime type, probably OS related problem. %s',
                guessed_type)
  return 'text/unknown'
      

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
  tree = dict(name=os.path.basename(path), path=path, children=[], kind='dir')

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
        tree['children'].append(dict(
            name=name, path=fn, kind='file',
            ext=os.path.splitext(fn)[1]))
  return tree


def check_match(file_path):
  for pattern in args.ignore_patterns:
    result = re.search(pattern, str(file_path))
    if result:
      return True


def _get_file_paths_flat(path):
  if check_match(path):
    return 
  leaves = []
  for root, dirs, files in os.walk(path, topdown=False):
    for name in files:
      leaves.append({
        'name': name,
        'path': os.path.join(root, name),
      }) 
  return leaves


@app.route('/')
@auth.login_required
def front_page_handler():
  return render_template(
      'index.html', tree=make_tree(_ROOT_DIR),
      html_content=args.front_page_message,
      note_extensions=args.note_extensions,
      mime_type='',
      file_paths_flat=json.dumps(_get_file_paths_flat(_ROOT_DIR)))


@app.route('/file')
@auth.login_required
def file_handler():
  path = request.args.get('f', '')
  if not path:
    return 'No path is given'
  path = path.strip()
  if not path.startswith(_ROOT_DIR):
    logging.info('no auth')
    return (
        'Not authorized to see this dir, must be under: ' +
        _ROOT_DIR)
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
      tree=make_tree(_ROOT_DIR), mime_type=mime_type,
      note_extensions=args.note_extensions,
      file_paths_flat=json.dumps(_get_file_paths_flat(_ROOT_DIR)))


@app.route('/api/get_content')
@auth.login_required
def api_get_content_handler():
  path = request.args.get('f', '')
  if not path.startswith(_ROOT_DIR):
    logging.info('no auth')
    return 'Not authorized to see this dir, must be under: %s' % _ROOT_DIR
  try:
    with open(path, 'r') as f:
      content = f.read()
    return jsonify({'result': 'success', 'content': content})
  except Exception as e:
    return jsonify({'result': 'smt went wrong ' + str(e)})


@app.route('/api/update', methods=['POST'])
@auth.login_required
def api_update_handler():
  updated_content = request.form.get('updated_content', '').strip()
  file_path = request.form.get('file_path', '').strip()
  if not file_path:
    return jsonify({'result': 'File path is empty'})
  
  if not file_path.startswith(_ROOT_DIR):
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
    parent_path = request.form.get('parent_path', '').strip()
    new_node_name = request.form.get('new_node_name', '').strip()
    if not parent_path or not new_node_name:
      return jsonify({
          'result': 'fail',
          'message': 'Path can not be empty',
      })
    new_node_name = new_node_name.strip()

    if not parent_path.startswith(_ROOT_DIR):
      return jsonify({
          'result': 'fail',
          'message': 'Unauth file modification',
      })

    if new_node_name.endswith('/'):
      path = os.path.join(parent_path, new_node_name)
      logging.info('Creating new node as dir %s', path)
      try:
        os.mkdir(path)
      except OSError:
        return jsonify({
            'result': 'fail',
            'message': 'Failed create this directory: ' +
            path +
            '. Make sure parent directory exists and  you have write '
            'access to the parent directory.',
            'entity': path,
        })
      else:
        return jsonify({
            'result':  'success', 
            'message': 'created the directory',
            'entity': path,
        })
    else:
      suffix = '' if new_node_name.endswith('.md') else '.md'
      path = os.path.join(parent_path, new_node_name + suffix)
      try:
        f = open(path, 'x')
      except OSError:
        return jsonify({
            'result':  'fail',
            'message': 'failed to create markdown file: ' + path,
            'entity': path,
        })
      else:
        return jsonify({
            'result':  'success',
            'message': 'created the directory: ' + path,
            'entity': path,
        })


@app.route('/api/move_file')
@auth.login_required
def api_move_handler():
  source_path = request.args.get('source_path', '')
  dest_dir = request.args.get('dest_dir', '')
  if not source_path.startswith(_ROOT_DIR) or not dest_dir.startswith(_ROOT_DIR):
    logging.info('no auth')
    return 'Not authorized to see this dir, must be under: %s' % _ROOT_DIR
  try:
    base_name = os.path.basename(source_path)
    dest_path = os.path.join(dest_dir, base_name)
    logging.info('Moving: %s %s %s %s', source_path, dest_path, base_name, dest_dir)
    if os.path.exists(dest_path):
      logging.error('Destination path, exists, renaming the moved file', dest_path)
      base_name, extension = os.path.splitext(dest_path)
      dest_path = base_name + '_' + datetime.datetime.now().strftime('%Y%m%d_%H%M') + extension
    shutil.move(source_path, dest_path)
    return jsonify({'result': 'success', 'source_path': source_path, 'dest_path': dest_path})
  except Exception as e:
    return jsonify({'result': 'smt went wrong ' + str(e)})


@app.route('/search')
@auth.login_required
def search_handler():
  query = request.args.get('query', '')
  if not query:
    return 'You need to search for something'
  # if not program_installed('ag') and not program_installed('ack'):
  #   return 'You should install either silver searcher (ag) or ack for fast search'

  # cmd = ''
  if program_installed('ag'):
    # ackmate mode for re-using same parsing logic.
    cmd = ['ag', query, _ROOT_DIR, '--ackmate', '--stats', '-m', '2']
    logging.info('Using ag for search')
  else:
    cmd = ['ack', query, _ROOT_DIR, '--column', '--heading'] 
    logging.info('Using ack for search')
  # TODO(hakanu): fallback to find.
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
  # ack doesn't have stats, ag has stats in the last 6 lines.
  tail = -6 if cmd[0] == 'ag' else -1
  delim = ';' if cmd[0] == 'ag' else ':'
  prefix = ':' if cmd[0] == 'ag' else ''

  stats_str = ' '.join(lines[tail:])
  in_file_started = False
  for line in lines[:tail]:
    print(line)
    # Check if the line starts with a number or a letter.
    # Number indicates that it's a file match starting.
    if line.startswith(prefix + _ROOT_DIR):
      fn = line
      in_file_results = []
      file_finished = False
      in_file_started = True
      continue
    elif in_file_started and delim in line:
      in_file_results.append({
          'snippet': line,
      })

      results.append({
        'file': fn.replace(':', ''),
        'matches': in_file_results,
      }) 

  html_body = ''
  return render_template(
      'index.html',
      search_results=results, query=query, stats=stats_str,
      tree=make_tree(_ROOT_DIR),
      note_extensions=args.note_extensions, mime_type='')


@app.route('/upload', methods=['POST'])
@auth.login_required
def file_upload_handler():
  # check if the post request has the file part
  if 'file' not in request.files:
    flash('No file part')
    return jsonif({'result': 'fail no file part'})
  file = request.files['file']
  # if user does not select file, browser also
  # submit an empty part without filename
  if file.filename == '':
    flash('No selected file')
    return jsonif({'result': 'fail no selected file'})
  if file and allowed_file(file.filename):
    filename = secure_filename(file.filename)
    base_name, extension = os.path.splitext(filename)
    dest_path = os.path.join(
        app.config['UPLOAD_FOLDER'], base_name + '_' + 
        datetime.datetime.now().strftime('%Y%m%d_%H%M') + extension)
    file.save(dest_path)
    logging.info('Upload is successful, refreshing the current page '
           'to show new file')
    return jsonify({
        'result': 'success',
        'message': 'File is successfully uploaded.',
        'entity': dest_path,
    })
  else:
    return jsonify({
        'result': 'fail',
        'message': 'probably the extension is not one of the allowed ones: '
        'gif, pdf, png, jpg',  
    })


def cli_main():
    """Used within the python package cli."""
    app.run(host=args.host, port=args.port)


if __name__ == '__main__':
  app.run(host=args.host, port=args.port)

