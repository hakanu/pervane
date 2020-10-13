from serve import app
from serve import args
import multiprocessing
import gunicorn.app.base


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


def main(as_module=False):
  options = {
      'bind': '%s:%s' % (args.host, args.port),
      'workers': number_of_workers(),
  }
  StandaloneApplication(app, options).run()

if __name__ == '__main__':
  cli_main()
