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
import pathlib
import re
import shutil
import subprocess
import sys

from jinja2 import Environment, BaseLoader
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, UserManager, UserMixin

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

mimetypes.init()

def str2bool(v):
  if isinstance(v, bool):
   return v
  if v.lower() in ('yes', 'true', 't', 'y', '1'):
    return True
  elif v.lower() in ('no', 'false', 'f', 'n', '0'):
    return False
  else:
    raise argparse.ArgumentTypeError('Boolean value expected.')

parser = argparse.ArgumentParser(description='Process input from user.')
parser.add_argument('--host', dest='host', default='0.0.0.0',
                    help='hostname to be binded')
parser.add_argument('--port', dest='port', default='5000',
                    help='port to be binded')
parser.add_argument('--dir', dest='root_dir',
                    default=os.environ.get("PERVANE_HOME", "./"),
                    help='Working folder to show the tree. If '
                         'PERVANE_HOME environment variable is '
                          'set and --dir is not provided, PERVANE_HOME is '
                          'used.')
parser.add_argument('--username', dest='username', default=None,
                    help='This is deprecated, please use cookie based login.')
parser.add_argument('--password', dest='password', default=None,
                    help='This is deprecated, please use cookie based login.')
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
parser.add_argument(
    '--allow_multi_user', type=str2bool, dest='allow_multi_user', default=False,
    help='Should pervane allow multiple users to see the same notes? Be careful.')
parser.add_argument(
    '--debug', type=str2bool, dest='debug', default=False,
    help='Show debug logs')
parser.add_argument(
    '--version', action='store_true', dest='version', default=False,
    help='Show version and exit')

args = parser.parse_args()

if args.version:
  # early return if only the version is asked.
  version_file =  os.path.join(os.path.dirname(os.path.realpath(__file__)), "version.txt")
  with open(version_file, "r") as version_fh:
    version = version_fh.readline()
    print('Pervane ', version)
    sys.exit()

# Log may not show up in non-debug mode.
print('loaded args %s', args)

if args.username or args.password:
  logging.error('WARNING: HTTP Basic Auth is deprecated, now Pervane has more '
		'cookie based login, please use that method.')

# We should always work with absolute path in order not to cause security issues
_WORKING_DIR = os.path.abspath(args.root_dir)
# Platform independent way of obtaining home folder.
_PERVANE_CONFIG_DIR = os.path.join(str(pathlib.Path.home()), '.pervane')
logging.info('config dir: ', _PERVANE_CONFIG_DIR)
if not os.path.exists(_PERVANE_CONFIG_DIR):
  logging.info('Pervane config dir does not exist, creating at %s',
               _PERVANE_CONFIG_DIR)
  os.mkdir(_PERVANE_CONFIG_DIR)
_SQLITE_PATH = 'sqlite:///' + os.path.join(
    _PERVANE_CONFIG_DIR, 'pervane.sqlite')
logging.info('db path: ', _SQLITE_PATH)

# This is for editor to render with higher fidelity with per
# language colors.
_FILE_MODE_DICT = {
    'md': 'text/html', 
    'txt': 'text/html', 
    'html': 'text/html', 
    'xhtml': 'text/html', 
    'js': 'javascript',
    'vue': 'javascript',
    'javascript': 'javascript',
    'jinja': 'javascript',
    'php': 'php',
    'xml': 'text/xml',
    'json': 'text/json',
    'java': 'java',
    'as': 'actionscript',
    'perl': 'perl',
    'go': 'go',
    'py': 'python',
    'c': 'c/c++',
    'cc': 'c/c++',
    'cpp': 'c/c++',
    'css': 'css',
    'rb': 'ruby',
 }


# Class-based application configuration
class ConfigClass(object):
  """ Flask application config """
  # Flask settings
  SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'
  # Flask-SQLAlchemy settings
  SQLALCHEMY_DATABASE_URI = _SQLITE_PATH 
  SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning
  # Flask-User settings
  USER_APP_NAME = "Pervane"      # Shown in and email templates and page footers
  USER_ENABLE_EMAIL = False      # Disable email authentication
  USER_ENABLE_USERNAME = True    # Enable username authentication
  USER_REQUIRE_RETYPE_PASSWORD = False    # Simplify register form
  USER_CORPORATION_NAME = 'Pervane'
  USER_COPYRIGHT_YEAR = '2020'
  USER_APP_VERSION = 'alpha'

logging.basicConfig(level=logging.DEBUG)
cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__, template_folder='templates')
cache.init_app(app)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app.config.from_object(__name__+'.ConfigClass')

# Initialize Flask-SQLAlchemy.
db = SQLAlchemy(app)

# Define the User data-model.
# NB: Make sure to add flask_user UserMixin !!!
class User(db.Model, UserMixin):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  active = db.Column('is_active', db.Boolean(), nullable=False,
                     server_default='1')

  # User authentication information. The collation='NOCASE' is required
  # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
  username = db.Column(db.String(100, collation='NOCASE'), nullable=False,
                       unique=True)
  password = db.Column(db.String(255), nullable=False, server_default='')
  email_confirmed_at = db.Column(db.DateTime())

  # User information
  first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False,
                         server_default='')
  last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False,
                         server_default='')
# Create all database tables
db.create_all()

class CustomUserManager(UserManager):
  # Override or extend the default register view method.
  def register_view(self):
    # If multi user signup is not allowed and there is a user.
    if not args.allow_multi_user and User.query.all():
      logging.info('A user already exists! Disabling registers')
      return ('There is already a user signed up, Pervane does not allow more users to sign up. '
              'Login here: <a href="/user/sign-in">Sign in</a>')
    return super().register_view()


# Setup Flask-User and specify the User data-model
user_manager = CustomUserManager(app, db, User)


def _check_pervane_needs_update():
  try:
    out = subprocess.Popen(
        'pip list --outdated'.split(' '), 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT)
    stdout,stderr = out.communicate()
    needs_update = True if 'pervane' in str(stdout) else False
    return {'needs_update': needs_update}
  except Exception as e:
    logging.error('Failed to check newest versions: ', str(e))
    # If for some reason, user is not using pip, don't crush on
    # this.
    return {'needs_update': True}


def _get_root_dir():
  return (
      _WORKING_DIR if not args.allow_multi_user else os.path.join(_WORKING_DIR, current_user.username)
  ) + os.path.sep


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


@cache.cached(timeout=args.cache_seconds, key_prefix='_make_tree')
def make_tree(path):
  """Higher level function to be used with cache."""
  return _make_tree(path)


def _get_workspace_path(fn):
  workspace_path = fn.replace(_get_root_dir(), '')
  # Prepend separator in case user enter root dir with / at the
  # end.
  if (not workspace_path.startswith(os.sep)):
    workspace_path = os.sep + workspace_path
  return workspace_path


def _make_tree(path):
  """Recursive function to get the file/dir tree.

  Can not be cached due to recursion.
  """
  tree = dict(name=os.path.basename(path),
              path=_get_workspace_path(path),
              children=[], kind='dir')

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
        workspace_path = _get_workspace_path(fn) 
        tree['children'].append(dict(
            name=name, path=workspace_path, kind='file', 
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
      leaves.append(
        os.path.join(root, name).replace(_get_root_dir(), os.path.sep)
      )
  return leaves


def _get_file_mode(path):
  print('getting file mode for ', path)
  if '.' in path:
    return _FILE_MODE_DICT.get(
        os.path.splitext(path)[1].replace('.', ''), 'text/html')
  return 'text/html'


@app.route('/api/check_updates')
@login_required
def api_check_updates():
  return jsonify(_check_pervane_needs_update())


@app.route('/')
@login_required
def front_page_handler():
  root_dir = _get_root_dir()
  if not os.path.exists(root_dir):
    logging.info('Initializing the root dir')
    os.mkdir(root_dir)
    
  return render_template(
      'index_vue.html', tree=make_tree(root_dir),
      html_content=args.front_page_message,
      note_extensions=args.note_extensions,
      mime_type='',
      file_paths_flat=json.dumps(_get_file_paths_flat(root_dir)),
      root_dir=root_dir,
      current_user=current_user,
      debug=args.debug,
      working_dir=_WORKING_DIR)


@app.route('/api/get_file')
@login_required
def api_get_file_handler():
  path = request.args.get('f', '')
  if not path:
    return 'No path is given'
  original_path = path

  # Even though passed path has separators, we get the last piece
  #  /hakuna/matata/yo => yo.
  # Trying to be defensive here against custom requests.

  # Get rid of that separator as first char and join with working dir.
  # /hakuna/test.md becomes /tmp/notes/hakuna/test.md
  path = os.path.join(_WORKING_DIR, path[1:])
  root_dir = _get_root_dir() 
  if not path.startswith(root_dir):
    logging.info('no auth')
    return ('Not authorized to see this dir')
  html_content = ''
  content = ''
  mime_type = get_mime_type(path)
  logging.info('mime_type: %s', mime_type)
  print('mime_type: ', mime_type)
  if (not mime_type.startswith('image/') and 
      not mime_type.startswith('video/') and
      not mime_type.startswith('text/') and
      # js source is not text for some reason. Need to be excepted.
      not mime_type == 'application/javascript'):
    return ('No idea how to show this file %s' %
            original_path)

  # Text is our main interest.
  if mime_type.startswith('text/'):
    try:
      with open(path, 'r') as f:
        content = f.read()
      html_content = content
    except Exception as e:
      logging.error('There is an error while reading: %s', str(e))
      return 'File reading failed.'
  elif mime_type.startswith('image/'):
    try:
      with open(path, 'rb') as f:
        content = base64.b64encode(f.read()).decode('ascii')
      html_content = content
    except Exception as e:
      logging.error('There is an error while reading: %s', str(e))
      return 'File reading failed.'
  return jsonify({
      'result': 'success',
      'content': html_content,
  })


@app.route('/api/get_tree')
@login_required
def api_get_tree_handler():
  root_dir = _get_root_dir()
  if not os.path.exists(root_dir):
    logging.info('Initializing the root dir')

  return jsonify({
      'result': 'success',
      'content': make_tree(root_dir)
  })


@app.route('/api/get_content')

@login_required
def api_get_content_handler():
  path = request.args.get('f', '').strip()
  if '..' in path:
    return 'You can not use relative paths'

  path = os.path.join(_WORKING_DIR, path[1:])
  root_dir = _get_root_dir()
  if not path.startswith(root_dir):
    logging.info('no auth')
    return 'Not authorized to see this dir' 

  # Obtain the file type to be rendered in editor from path.
  file_mode = _get_file_mode(path)

  try:
    with open(path, 'r') as f:
      content = f.read()
    return jsonify({
        'result': 'success',
        'content': content,
        'file_mode': file_mode,
    })
  except Exception as e:
    return jsonify(
      {'result': 'smt went wrong ' + str(e)})


@app.route('/api/update', methods=['POST'])
@login_required
def api_update_handler():
  updated_content = request.json.get('updated_content', '').strip()
  root_dir = _get_root_dir()
  file_path = os.path.join(
      _WORKING_DIR, request.json.get('file_path', '').strip()[1:])
  if not file_path:
    return jsonify({'result': 'File path is empty'})
  
  if not file_path.startswith(root_dir):
    return jsonify({'result': 'Unauth file modification'})

  if not updated_content:
    return jsonify({'result': 'File content is empty'})
  try:
    with open(file_path, 'w') as f:
      f.write(updated_content)
  except Exception as e:
    return jsonify({'result': 'update failed', 'error': str(e)})
  return jsonify({'result': 'success'}) 


@app.route('/api/add_node', methods=['POST'])
@login_required
def add_node_handler():
  root_dir = _get_root_dir()

  # Parent path comes like /username or / so the real parent path needs to be built.
  # Remove / from the GET param.
  parent_path = os.path.join(
      _WORKING_DIR, request.json.get('parent_path', '').strip()[1:])

  # Eliminate file separator.
  new_node_name = request.json.get('new_node_name', '').strip()
  is_dir = False
  if new_node_name.endswith(os.path.sep):
    is_dir = True
    # Strip the /.
    new_node_name = new_node_name[:-1]
  if not parent_path or not new_node_name:
    return jsonify({
        'result': 'fail',
        'message': 'Path can not be empty',
    })
  new_node_name = new_node_name.strip()

  if not parent_path.startswith(root_dir):
    return jsonify({
        'result': 'fail',
        'message': 'Unauth file modification',
    })

  if is_dir:
    path = os.path.join(parent_path, new_node_name)
    logging.info('Creating new node as dir %s', path)
    try:
      os.mkdir(path)
    except OSError:
      return jsonify({
          'result': 'fail',
          'message': (
              'Failed create this directory.' 
              'Make sure parent directory exists and you have write '
              'access to the parent directory.'),
          'entity': '',  # Don't reveal failed path for security.
      })
    else:
      return jsonify({
          'result':  'success', 
          'message': 'created the directory',
          'type': 'dir',
          'entity': os.path.join(
            path, os.path.sep).replace(_WORKING_DIR, ''),
      })
  else:
    suffix = '' if new_node_name.endswith('.md') else '.md'
    path = os.path.join(parent_path, new_node_name + suffix)
    try:
      f = open(path, 'x')
    except OSError:
      return jsonify({
          'result':  'fail',
          'message': 'failed to create markdown file.',
          'entity': '',  # Don't reveal path.
      })
    else:
      return jsonify({
          'result':  'success',
          'message': 'created the directory: ' + path.replace(
              _WORKING_DIR, ''),
          'type': 'file',
          'entity': path.replace(_WORKING_DIR, ''),
      })


@app.route('/api/move_file')
@login_required
def api_move_handler():
  source_path = os.path.join(
      _WORKING_DIR, request.args.get('source_path', '').strip()[1:])
  root_dir = _get_root_dir()
  dest_dir = os.path.join(
      _WORKING_DIR, request.args.get('dest_dir', '').strip()[1:])
  if (not source_path.startswith(root_dir) or
      not dest_dir.startswith(root_dir)):
    logging.info('no auth')
    return 'Not authorized to see this dir.'
  try:
    base_name = os.path.basename(source_path)
    dest_path = os.path.join(dest_dir, base_name)
    logging.info('Moving: %s %s %s %s', source_path, dest_path, 
                 base_name, dest_dir)
    if os.path.exists(dest_path):
      logging.error('Destination path, exists, renaming the moved file', 
                    dest_path)
      base_name, extension = os.path.splitext(dest_path)
      dest_path = base_name + '_' + datetime.datetime.now().strftime(
          '%Y%m%d_%H%M') + extension
    shutil.move(source_path, dest_path)
    return jsonify({
        'result': 'success', 
        'source_path': source_path, 
        'dest_path': dest_path
    })
  except Exception as e:
    return jsonify({'result': 'smt went wrong '})


@app.route('/api/search')
@login_required
def api_search_handler():
  root_dir = _get_root_dir()
  query = request.args.get('query', '')
  if not query:
    return 'You need to search for something'

  cmd = ''
  if program_installed('ag'):
    # ackmate mode for re-using same parsing logic.
    cmd = ['ag', query, root_dir, '--ackmate', '--stats', '-m', '2']
    logging.info('Using ag for search')
  else:
    cmd = ['ack', query, root_dir, '--column', '--heading'] 
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
    # Check if the line starts with a number or a letter.
    # Number indicates that it's a file match starting.
    if line.startswith(prefix + root_dir):
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
        'file': fn.replace(':', '').replace(_WORKING_DIR, ''),
        'matches': in_file_results,
      }) 

  return jsonify({
      'result': 'success',
      'content': {
        'results': results,
        'stats': stats_str,
      }
  })


@app.route('/upload', methods=['POST'])
@login_required
def file_upload_handler():
  root_dir = _get_root_dir()
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
        root_dir, base_name + '_' + 
        datetime.datetime.now().strftime('%Y%m%d_%H%M') + extension)
    file.save(dest_path)
    logging.info('Upload is successful, refreshing the current page '
           'to show new file')
    return jsonify({
        'result': 'success',
        'message': 'File is successfully uploaded.',
        'entity': dest_path.replace(_WORKING_DIR, ''),
    })
  else:
    return jsonify({
        'result': 'fail',
        'message': 'probably the extension is not one of the allowed ones: '
        'gif, pdf, png, jpg',  
    })


def cli_main():
  """Used within the python package cli."""
  app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
  print('app run with ', args.host, args.port)
  app.run(host=args.host, port=args.port, debug=args.debug)
