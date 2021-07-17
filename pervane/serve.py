"""Simple plain text based note taking app to serve and files with hierarchy.

# Dependencies:

- Flask as python server.
- Vue.js for UI (I'm not a js ninja so don't beat me up on that
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

Cookie based user login support is provided by Flask-User package using a sqlite
db living in ~/.pervane folder (similar path for windows too.)

# Init:
virtualenv -p python3 env
source env/bin/activate
pip3 install -r requirements.txt

# Run simple:
python3 serve.py --dir=example/ --debug=true
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
from operator import itemgetter

from jinja2 import Environment, BaseLoader
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, flash
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, UserManager, UserMixin

from werkzeug.routing import BaseConverter
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from atomicfile import AtomicFile

mimetypes.init()

def _str2bool(v):
  if isinstance(v, bool):
   return v
  if v.lower() in ('yes', 'true', 't', 'y', '1'):
    return True
  elif v.lower() in ('no', 'false', 'f', 'n', '0'):
    return False
  else:
    raise argparse.ArgumentTypeError('Boolean value expected.')

parser = argparse.ArgumentParser(description='Process input from user.')
parser.add_argument('--host', dest='host',
                    default=os.environ.get('PERVANE_HOST', '0.0.0.0'),
                    help='hostname to be binded')
parser.add_argument('--port', dest='port',
                    default=os.environ.get('PERVANE_PORT', '5000'),
                    help='port to be binded')
parser.add_argument('--dir', dest='root_dir',
                    default=os.environ.get('PERVANE_HOME', './'),
                    help='Working folder to show the tree. If '
                         'PERVANE_HOME environment variable is '
                          'set and --dir is not provided, PERVANE_HOME is '
                          'used.')
parser.add_argument('--config_dir', dest='config_dir',
                    default=os.environ.get('PERVANE_CONFIG_HOME',
                    os.path.join(str(pathlib.Path.home()), '.pervane')),
                    help='Directory to keep internal files of pervane.')
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
             '.*.sqlite', '.*.plist'],
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
    '--allow_multi_user', type=_str2bool, dest='allow_multi_user',
    default=os.environ.get('PERVANE_ALLOW_MULTI_USER', 'False'),
    help='Should pervane allow multiple users to see the same notes? Be careful.')
parser.add_argument(
    '--debug', type=_str2bool, dest='debug',
    default=os.environ.get('PERVANE_DEBUG', 'False'),
    help='Show debug logs')
parser.add_argument(
    '--version', action='store_true', dest='version', default=False,
    help='Show version and exit')

args = parser.parse_args()

if args.version:
  # early return if only the version is asked.
  version_file =  os.path.join(os.path.dirname(os.path.realpath(__file__)), 'version.txt')
  with open(version_file, 'r') as version_fh:
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
_PERVANE_CONFIG_DIR = os.path.abspath(args.config_dir)
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

# Regex url matcher.
class regex_converter(BaseConverter):
  def __init__(self, url_map, *items):
    super(regex_converter, self).__init__(url_map)
    self.regex = items[0]

app.url_map.converters['regex'] = regex_converter 

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
    logging.error('Failed to check newest versions', exc_info=True)
    # If for some reason, user is not using pip, don't crush on
    # this.
    return {'needs_update': False}


def _get_root_dir(trailing_separator = True):
  path = _WORKING_DIR if not args.allow_multi_user else os.path.join(_WORKING_DIR, current_user.username)
  return path + os.path.sep if trailing_separator else path


def _is_program_installed(binary):
  rc = subprocess.call(['which', binary])
  if rc == 0:
    return True 
  else:
    return False


def _is_filename_allowed(filename):
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


def _get_workspace_path(path):
  """Shortens the given absolute path by removing the root dir.
  
  For instance, /home/user/pervane/note-dir/note1.md becomes
  /note-dir/note1.md"""
  path = path.replace(_get_root_dir(trailing_separator=False), '')
  return path if path.startswith(os.sep) else os.path.join(os.sep, path)


def _make_tree(path):
  """Recursive function to get the file/dir tree.

  Can not be cached due to recursion.
  """
  if is_ignored(path):
   return

  this_node = dict(name=os.path.basename(path),
              path=_get_workspace_path(path),
              children=[], kind='dir')

  try:
    children = os.listdir(path)
  except OSError:
    pass #ignore errors
  else:
    for child_name in children:
      child_path = os.path.join(path, child_name)

      if is_ignored(child_path):
        continue

      if os.path.isdir(child_path):
        this_node['children'].append(_make_tree(child_path))
      else:
        this_node['children'].append(dict(
          name=child_name, path=_get_workspace_path(child_path),
          kind='file', ext=os.path.splitext(child_path)[1]))
  
  if len(this_node['children']) > 0:
    # Sort by two keys.
    # Kind is for sorting the directories first.
    # Name is for natural alphabetical order within directories and files 
    # separately.
    this_node['children'] = sorted(
        this_node['children'], key=itemgetter('kind', 'name'))
  return this_node 


def is_ignored(file_path):
  for pattern in args.ignore_patterns:
    result = re.search(pattern, str(file_path))
    if result:
      return True


def _get_file_paths_flat(path):
  if is_ignored(path):
    return 
  leaves = []
  root_dir = _get_root_dir(trailing_separator=False)
  for root, dirs, files in os.walk(path, topdown=False):
    for name in files:
      leaves.append(
        os.path.join(root, name).replace(root_dir, '')
      )
  return leaves


def _get_file_mode(path):
  if '.' in path:
    return _FILE_MODE_DICT.get(
        os.path.splitext(path)[1].replace('.', ''), 'text/html')
  return 'text/html'


def _get_file_mod_time(path):
  mod_secs = os.path.getmtime(path)
  return datetime.datetime.fromtimestamp(mod_secs).strftime('%Y-%m-%d %H:%M:%S')


def _get_request_param(arg_name):
  return request.args.get(arg_name, '').strip()


def _get_request_json(arg_name):
  return request.json.get(arg_name, '').strip()


def _to_real_path(parent_path, relative_path):
  """Creates an absolute path from given paths.

  If there is any . or .. in the merged path, it is evaluated and
  the real path is generated. For instance, /home/user/pervane and
  /../../file1 results in /home/file1. 

  Heading separator of relative path is ignored.
  """
  start_index = 1 if relative_path.startswith(os.sep) else 0
  absoluate_path = os.path.join(parent_path, relative_path[start_index:])
  return os.path.realpath(absoluate_path)


def _get_real_path(workspace_path):
  """Converts the given workspace path into an absolute path.

  A tuple of a real path and an error is returned. In this tuple, either 
  the real path or error is present. The error is present in the returned tuple
  either if no workspace dir is given or the generated real path is not under 
  the working directory.
  """
  if not workspace_path:
    return (None, 'No path is given')

  root_dir = _get_root_dir(trailing_separator=False)
  path = _to_real_path(root_dir, workspace_path)

  return (path, None) if path.startswith(root_dir) else (None, 'Not authorized')


def _get_new_node_name(new_node_name):
  """Parses the given node name to either a file name or a directory name.

  A triplet of a file name, a directory name, and an error is returned. In this
  triplet, either the file name, directory name, or error is present. If there
  is no '/' in the given node name, it is considered as a file. If there is no
  extension in the file name, '.md' is appended to it.

  An error is returned if node node is missing, or the parsed directory or file
  name is equal to '.' or '..', or the file name contains an invalid extension.
  """
  if not new_node_name:
    return (None, None, "empty file name!")

  new_node_name = new_node_name.strip()

  if new_node_name.startswith(os.path.sep):
    new_node_name = new_node_name[1:].strip()

  if not new_node_name:
    return (None, None, 'empty file name!')

  if new_node_name.endswith(os.path.sep):
    # Eliminate the tailing file separator.
    dir_name = new_node_name[:-1]
    if not dir_name or  dir_name == '.' or dir_name == '..':
      return (None, None, 'invalid directory name: ' + dir_name)

    return (dir_name, None, None)

  if new_node_name == '.' or new_node_name == '..':
    return (None, None, 'invalid file name: ' + new_node_name)

  if '.' not in new_node_name:
    # Append .md if there is no extension.
    file_name = new_node_name + '.md'
  else:
    file_name = new_node_name

  return (None, file_name, None)


def _failure_json(err):
  if err == 'success':
    raise ValueError
  return jsonify({'result' : err})


@app.context_processor
def inject_dict_for_all_templates():
  return dict(
      logged_in_user=current_user)


@app.route('/api/check_updates')
@login_required
def api_check_updates():
  # return jsonify(_check_pervane_needs_update())
  return jsonify({})


@app.route('/')
@login_required
def front_page_handler():
  root_dir = _get_root_dir()
  if not os.path.exists(root_dir):
    logging.info('Initializing the root dir')
    os.mkdir(root_dir)
    
  return render_template(
      'index.html', tree=make_tree(root_dir),
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
  requested_path = _get_request_param('f')
  path, err = _get_real_path(requested_path)

  if err:
    return _failure_json('invalid path: ' + err)

  mime_type = get_mime_type(path)
  logging.info('mime_type: %s', mime_type)
  if (not mime_type.startswith('image/') and 
      not mime_type.startswith('video/') and
      not mime_type.startswith('text/') and
      # js source is not text for some reason. Need to be excepted.
      not mime_type == 'application/javascript'):
    return jsonify({'result' : ('No idea how to show this file %s' %
            requested_path)})

  try:
    html_content = ''
    # Text is our main interest.
    if mime_type.startswith('text/'):
      with open(path, 'r') as f:
        html_content = f.read()
    elif mime_type.startswith('image/'):
      with open(path, 'rb') as f:
        html_content = base64.b64encode(f.read()).decode('ascii')

    # TODO [basri] mime_type could be video or js here. we return nothing in this case?
    mod_time = _get_file_mod_time(path)

    return jsonify({
      'result': 'success',
      'content': html_content,
      'mod_time': mod_time
    })
  except Exception as e:
    logging.error('There is an error while reading: %r', path, exc_info=True)
    # Don't leak the absolute path.
    return _failure_json(('Reading %s failed' % requested_path))


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
  requested_path = _get_request_param('f')
  path, err = _get_real_path(requested_path)

  if err:
    return _failure_json('invalid path: ' + err)

  # Obtain the file type to be rendered in editor from path.
  file_mode = _get_file_mode(requested_path)

  try:
    with open(path, 'r') as f:
      content = f.read()
      mod_time = _get_file_mod_time(path)

    return jsonify({
        'result': 'success',
        'content': content,
        'file_mode': file_mode,
        'mod_time': mod_time
    })
  except Exception as e:
    logging.error('There is an error while reading: %r', path, exc_info=True)
    # Don't leak the absolute path.
    return _failure_json(('Reading %s failed' % requested_path))


@app.route('/api/update', methods=['POST'])
@login_required
def api_update_handler():
  # TODO [basri] is it a good idea to strip spaces from user's own text?
  updated_content = _get_request_json('updated_content')
  if not updated_content:
    return _failure_json('File content is empty')

  requested_path = _get_request_json('file_path')
  path, err = _get_real_path(requested_path)
  if err:
    return _failure_json(err)

  try:
    with AtomicFile(path, 'w') as f:
      f.write(updated_content)
      
    return jsonify({'result': 'success'})
  except Exception as e:
    logging.error('There is an error while writing: %r', path, exc_info=True)
    # Don't leak the absolute path.
    return _failure_json(('Writing %s failed' % requested_path))


@app.route('/api/add_node', methods=['POST'])
@login_required
def add_node_handler():
  root_dir = _get_root_dir()

  parent_path, err = _get_real_path(_get_request_json('parent_path'))
  if err:
    return _failure_json(err)

  dir_name, file_name, err = _get_new_node_name(
    _get_request_json('new_node_name'))

  if err:
    return _failure_json(err)

  if dir_name:
    new_dir_path = _to_real_path(parent_path, dir_name)
    logging.info('Creating new dir: %s', new_dir_path)
    try:
      os.mkdir(new_dir_path)
    except OSError as e:
      logging.error('Could not create new dir: %s. Error: %s',
                  new_dir_path, str(e))
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
          'entity': _get_workspace_path(new_dir_path),
      })
  else:
    new_file_path = _to_real_path(parent_path, file_name)
    logging.info('Creating new file: %s', new_file_path)
    try:
      f = open(new_file_path, 'x')
    except OSError as e:
      logging.error('Could not create new file: %s. Error: %s',
                    new_file_path, str(e))
      return jsonify({
          'result':  'fail',
          'message': 'failed to create markdown file.',
          'entity': '',  # Don't reveal path.
      })
    else:
      return jsonify({
          'result':  'success',
          'message': 'created the file.',
          'type': 'file',
          'entity': _get_workspace_path(new_file_path),
      })


@app.route('/api/move_file')
@login_required
def api_move_handler():
  source_path, err1 = _get_real_path(_get_request_param('source_path'))
  dest_dir, err2 = _get_real_path(_get_request_param('dest_dir'))

  if err1 or err2:
    logging.info('no auth')
    return _failure_json('Not authorized')

  try:
    base_name = os.path.basename(source_path)
    dest_path = _to_real_path(dest_dir, base_name)

    logging.info('Moving: %s %s %s %s', source_path, dest_path,
                 base_name, dest_dir)
    if os.path.exists(dest_path):
      logging.error('Destination path exists, renaming the moved file',
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
    logging.error('There is an error while moving %r to %r',
                  source_path, dest_dir, exc_info=True)
    return _failure_json('smt went wrong')


@app.route('/api/search')
@login_required
def api_search_handler():
  query = _get_request_param('query')
  if not query:
    return _failure_json('You need to search for something')

  root_dir = _get_root_dir()
  cmd = ''
  if _is_program_installed('ag'):
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

  # TODO [basri] what if error occurs?

  # Convert output from binary to string.
  output = output.decode('utf-8')
  lines = output.split('\n')
  results = []
  in_file_results = []
  fn = ''
  file_finished = False

  # Extract stats tail first.
  # ack doesn't have stats, ag has stats in the last 6 lines.
  tail, delim, prefix = (-6, ';', ':') if cmd[0] == 'ag' else (-1, ':', '')

  stats_str = ' '.join(lines[tail:])
  in_file_started = False
  for line in lines[:tail]:
    if line and line[-1] == '\0':
      # get rid of NULL terminator
      line = line[:-1]

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
        'file': _get_workspace_path(fn.replace(':', '')),
        'matches': in_file_results,
      }) 

  return jsonify({
      'result': 'success',
      'content': {
        'results': results,
        'stats': stats_str,
      }
  })


@app.route('/api/glob')
@login_required
def api_glob_handler():
  root_dir = _get_root_dir()
  glob_root, err = _get_real_path(_get_request_param('f'))
  if err:
    return _failure_json('You need to glob in a directory')

  # TODO(hakanu): would os.walk be better?
  raw_files = os.listdir(glob_root)
  files = []
  dirs = []
  for raw_file in raw_files:
    # Create an actual path to check if it's a directory.
    raw_file = _to_real_path(glob_root, raw_file)
    if os.path.isdir(raw_file):
      dirs.append(raw_file.replace(_WORKING_DIR, ''))
      continue
    else:
      files.append(raw_file.replace(_WORKING_DIR, ''))

  return jsonify({
      'result': 'success',
      'content': {
        'results': {
          'dirs': dirs,
          'files': files,
        },
      }
  })
  


@app.route('/upload', methods=['POST'])
@login_required
def file_upload_handler():
  root_dir = _get_root_dir()
  # check if the post request has the file part
  if 'file' not in request.files:
    flash('No file part')
    return _failure_json('fail no file part')
  file = request.files['file']
  # if user does not select file, browser also
  # submit an empty part without filename
  if file.filename == '':
    flash('No selected file')
    return _failure_json('fail no selected file')
  if file and _is_filename_allowed(file.filename):
    filename = secure_filename(file.filename)
    base_name, extension = os.path.splitext(filename)
    filename = base_name + '_' + datetime.datetime.now().strftime('%Y%m%d_%H%M') + extension

    dest_path, err = _get_real_path(filename)

    if err:
      return _failure_json('No auth')

    file.save(dest_path)
    logging.info('Upload is successful, refreshing the current page '
           'to show new file')
    return jsonify({
        'result': 'success',
        'message': 'File is successfully uploaded.',
        'entity': filename,
    })
  else:
    return _failure_json('probably the extension is not one of the allowed ones: '
        'gif, pdf, png, jpg')


@app.route('/_img/<path:file_path>', methods=['GET'])
@login_required
def static_file_handler(file_path):
  """Incoming file path is under users working dir.

  This is not intended to be used for css and js.
  for them normal workflow from flask is used with /static prefix.

  eg. (for default run with --dir=./example)
  http://localhost:5001/img/test/images/apple-touch-icon.png
  http://localhost:5001/img/test/test_video/video.mp4
  """

  path, err = _get_real_path(file_path)
  if err:
    return _failure_json(err)

  return send_from_directory(_get_root_dir(), file_path)


# TODO(hakanu): Slowly get rid of this in favor of production gunicorn.
def cli_main():
  """Used within the python package cli."""
  app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
  app.run(host=args.host, port=args.port, debug=args.debug)
