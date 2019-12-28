import sys
import glob

from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def hello(name=None):
    from pathlib import Path

    for filename in Path('.').rglob('*.md'):
        print(filename)
    return render_template('index.html', name=name)

