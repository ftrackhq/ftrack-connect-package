# :coding: utf-8
# :copyright: Copyright (c) 2014 ftrack

import sys
import os
import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

'''
Fix for missing sys.stderr when building Win32GUI cx_freeze
see: https://github.com/marcelotduarte/cx_Freeze/issues/60
'''

try:
    sys.stderr.write("\n")
    sys.stderr.flush()
except Exception:
    import sys
    import http.server

    class SysWrapper(object):
        def __getattribute__(self, item):
            if item is 'stderr':
                class DummyStream:
                    def __init__(self): pass

                    def write(self, *args, **kwargs):
                        logger.info(args)

                return DummyStream()
            return getattr(sys, item)


    http.server.sys = SysWrapper()


def set_environ_default(name, value):
    '''Set environment variable *name* and *value* as default.'''
    if name in os.environ:
        logger.debug(
            u'{0} already configured in environment: {1}'.format(
                name, value
            )
        )

    os.environ.setdefault(name, value)


resource_path = os.path.abspath(
    os.path.join(
        os.path.dirname(sys.executable), 'resource'
    )
)

if sys.platform == "darwin":
    exec_path = Path(os.path.dirname(sys.executable))
    resource_path = os.path.abspath(
        os.path.join(
            str(exec_path.parent), 'Resources', 'resource'
        )
    )

set_environ_default(
    'FTRACK_EVENT_PLUGIN_PATH',
    os.path.abspath(
        os.path.join(
            resource_path, 'hook'
        )
    )
)

# Set the path to certificate file in resource folder. This allows requests
# module to read it outside frozen zip file.
set_environ_default(
    'REQUESTS_CA_BUNDLE',
    os.path.abspath(
        os.path.join(
            resource_path, 'cacert.pem'
        )
    )
)

# Websocket-client ships with its own cacert file, we however default
# to the one shipped with the requests library.
set_environ_default(
    'WEBSOCKET_CLIENT_CA_BUNDLE',
    os.environ.get('REQUESTS_CA_BUNDLE')
)

# The httplib in python +2.7.9 requires a cacert file.
set_environ_default(
    'SSL_CERT_FILE',
    os.environ.get('REQUESTS_CA_BUNDLE')
)

# handle default connect and event plugin paths
ftrack_connect_plugin_paths = [
    os.path.abspath(
        os.path.join(
            resource_path,
            'connect-standard-plugins'
        )
    )
]

if 'FTRACK_CONNECT_PLUGIN_PATH' in os.environ:
    ftrack_connect_plugin_paths.append(
        os.environ['FTRACK_CONNECT_PLUGIN_PATH']
    )

os.environ['FTRACK_CONNECT_PLUGIN_PATH'] = os.path.pathsep.join(
    ftrack_connect_plugin_paths
)

# handle default event plugin paths
ftrack_event_plugin_paths = [
    os.path.abspath(
            os.path.join(
                resource_path, 'hook'
            )
        )
]

if 'FTRACK_EVENT_PLUGIN_PATH' in os.environ:
    ftrack_event_plugin_paths.append(
        os.environ['FTRACK_EVENT_PLUGIN_PATH']
    )

os.environ['FTRACK_EVENT_PLUGIN_PATH'] = os.path.pathsep.join(
    ftrack_event_plugin_paths
)

set_environ_default(
    'FTRACK_CONNECT_PACKAGE_RESOURCE_PATH',
    resource_path
)

import ftrack_connect.__main__


def _validatePythonScript(path):
    '''Validate if *path* is a valid python script.'''
    return path and path.endswith('.py') and os.path.exists(path)

import datetime
import requests
import zipfile
import subprocess
ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
DOWNLOAD_PLUGIN_PATH = os.path.join(
    ROOT_PATH, 'plugin-downloads-{0}'.format(
        datetime.datetime.now().strftime('%y-%m-%d-%H-%M-%S')
    )
)

class PythonAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)

    def _get_dependency_link(self, name, version):
        #TODO: look on a json file posted in a server to match paths
        # we can do build, install or download a prebuild one from amazon
        version='1.0.0-b2'
        plugin_url = (
            'https://bitbucket.org/ftrack/ftrack-connect-pipeline/get/{0}.zip'
            '#egg=ftrack-connect-{0}'
        ).format(version)
        return plugin_url

    def download_plugin(self, plugin_url, plugin_name, plugin_version):

        plugin_zip_name = "{}-{}.zip".format(plugin_name, plugin_version)
        temp_path = os.path.join(DOWNLOAD_PLUGIN_PATH, plugin_name)
        plugin_zip_path = os.path.join(temp_path, plugin_zip_name)
        logging.info(
            'Downloading url {0} to {1}'.format(
                plugin_url,
                temp_path
            )
        )
        os.makedirs(temp_path)
        response = requests.get(plugin_url)
        response.raise_for_status()

        if response.status_code != 200:
            raise ValueError(
                'Got status code not equal to 200: {0}'.format(
                    response.status_code
                )
            )

        with open(plugin_zip_path, 'wb') as package_file:
            package_file.write(response.content)

        target = plugin_zip_path.replace('.zip', '')
        extract_folder = os.path.join(DOWNLOAD_PLUGIN_PATH, target)
        with zipfile.ZipFile(plugin_zip_path, 'r') as myzip:
            myzip.extractall(target)

        return os.path.join(extract_folder, os.listdir(extract_folder)[0])

    def install_plugin(self, plugin_folder):
        os.system('cd "{}" && python setup.py install'.format(plugin_folder))

    def build_plugin(self, plugin_folder):
        build_plugin = plugin_folder.split("/")[-2]
        command = (
            'cd "{}" && python setup.py build_plugin && '
            'cp -r "build/{}" "/Users/lluisftrack/Library/Application Support/ftrack-connect-plugins/"'.format(
            plugin_folder, build_plugin
        )
        )
        subprocess.check_output(command, shell=True)

    def install_package(self, package_name, package_version=None):
        if package_version:
            os.system('pip install {}=={}'.format(package_name, package_version))
        else:
            os.system('pip install {}'.format(package_name))

    def __call__(self, parser, namespace, values, option_string=None):
        print('%r %r %r' % (namespace, values, option_string))
        name = None
        version = None
        if values.find("==") != -1:
            name, version = values.split("==")
        else:
            name = values
        if option_string == '-ip' or option_string =='--install_plugin':
            # exec(values)
            # temporal code
            name = 'ftrack-connect-pipeline'
            version='1.0.0-b2'


            plugin_url = self._get_dependency_link(name, version)
            plugin_folder = self.download_plugin(plugin_url, name, version)

            #TODO: uncomment this and comment the build_plugin to install
            # the plugin in the connect environment

            # self.install_plugin(plugin_folder)
            self.build_plugin(plugin_folder)

        elif option_string == '-ipkg' or option_string =='--install_python_package':
            self.install_package(name, version)

        setattr(namespace, self.dest, values)



if __name__ == '__main__':
    arguments = sys.argv[1:]

    if sys.platform == "darwin" and getattr(sys, 'frozen', False):
        # Filter out PSN (process serial number) argument passed by OSX.
        arguments = [
            argument for argument in arguments
            if '-psn_0_' not in argument
        ]

    parser = argparse.ArgumentParser()

    parser.add_argument(
        'script',
        help='Path to python script to execute.',
        default='',
        nargs='?'
    )

    parser.add_argument(
        '-ip', '--install_plugin',
        required=False,
        help='Install connect plugin.',
        action=PythonAction
    )

    parser.add_argument(
        '-ipkg', '--install_python_package',
        required=False,
        help='Install python plugin.',
        action=PythonAction
    )

    parser.add_argument(
        '-ui', '--uninstall_python_package',
        required=False,
        help='Unintsall python package.',
        action=PythonAction
    )

    parser.add_argument(
        '-up', '--uninstall_plugin',
        required=False,
        help='Unintsall python plugin.',
        action=PythonAction
    )

    parser.add_argument(
        '-s', '--silent',
        help='Start connect window in hidden mode.',
        action='store_true'
    )

    parsedArguments, unknownArguments = parser.parse_known_args(arguments)

    exec_args = [
        '-ipkg', '--install_python_package', '-ip', '--install_plugin', '-ui',
        '--uninstall_python_package', '-up', '--uninstall_plugin'
    ]
    executable_args = []
    for idx in range(len(arguments)):
        if (
                arguments[idx] in exec_args or
                arguments[idx - 1] in exec_args
        ):
            continue
        executable_args.append(arguments[idx])

    # If first argument is an executable python script, execute the file.
    if (
        parsedArguments.script and
        _validatePythonScript(parsedArguments.script)
    ):
        exec(open(parsedArguments.script).read())
        raise SystemExit()

    raise SystemExit(
        ftrack_connect.__main__.main(arguments=executable_args)
    )
