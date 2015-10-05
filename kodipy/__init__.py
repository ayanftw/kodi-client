import configparser
import os
import requests
from functools import partial
from pprint import pformat


class KodiInterface():

    options = {
        'host': 'localhost',
        'port': 8080,
        'username': '',
        'password': '',
    }

    def __init__(self, configfile=None, sectionname=None,
                 *args, **kwargs):
        self.config = self.get_config(configfile)
        # use either 'default' or the first section from the config file
        self.name = (sectionname if sectionname in self.config.sections()
                     else self.config.sections()[0])
        self.config[self.name].update({
            x: kwargs.get(x)
            for x in self.options.keys()
            if kwargs.get(x, None) is not None
        })

    def get_defaultconfig(self):
        return os.path.join(os.path.expanduser('~'), '.kodi-cli')

    def get_config(self, configfile=None):
        if configfile is None or not os.access(configfile, os.R_OK):
            configfile = self.get_defaultconfig()
        config = configparser.ConfigParser()
        config['DEFAULT'] = self.options
        config.read(configfile)
        return config

    def call_command(self, command=None, params=None, *args, **kwargs):
        cfg = self.config[self.name]
        data = {
            'jsonrpc': '2.0',
            'id': 'kodi-cli',
            'method': command,
        }
        if params is None:
            params = {}
        params.update(kwargs)
        data['params'] = params
        try:
            req = requests.post(
                'http://{host}:{port}/jsonrpc'.format(**cfg),
                json=data,
                headers={'content-type': 'application/json'},
                timeout=2,
            )
            req.raise_for_status()
            data = req.json()
            return data['result']
        except KeyError:
            return data['error']
        except requests.Timeout:
            raise SystemExit("request timed out")
        except requests.HTTPError:
            raise SystemExit("{} - {}".format(req.status_code, req.reason))

    def introspect(self):

        class APIGroup(object):
            pass

        class APICommand():

            def __init__(self, func, desc):
                self.func = func
                self.desc = desc

            def __call__(self, *args, **kwargs):
                return self.func(*args, **kwargs)

            def __doc__(self):
                return (
                    "{}\n"
                    "Params: {}\n"
                    "Returns: {}\n".format(
                        self.desc['description'],
                        pformat(self.desc['params']),
                        pformat(self.desc['returns']),
                    )
                )

        def setter(name, desc):
            mod, func = name.split('.')
            if not hasattr(self, mod):
                setattr(self, mod, APIGroup())
            module = getattr(self, mod)
            setattr(module, func,
                    APICommand(partial(self.call_command, command=name), desc))

        api = self.call_command('JSONRPC.Introspect')
        for method, desc in api.get('methods', {}).items():
            setter(method, desc)
