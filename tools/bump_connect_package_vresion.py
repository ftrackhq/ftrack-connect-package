import os
import re
import copy
import logging
import datetime
import tempfile
import semantic_version
from distutils.util import strtobool

from fabric import (
    api
)

logger = logging.getLogger(
    __name__
)

logging.basicConfig(
    level=logging.INFO
)

def update_version(repo, branch='master', version=None, push=False):
    checkout_directory = tempfile.mkdtemp()

    with api.lcd(checkout_directory):
        logger.info(
            'checkout {0} from {1} to {2}'.format(
                branch, repo, checkout_directory
            )
        )

        checkout_name = 'checkout'

        api.local(
            'git clone -b {0} {1} {2}'.format(
                branch, repo, checkout_name
            )
        )

        root_directory = os.path.join(
            checkout_directory, checkout_name
        )

        with api.lcd(root_directory):
            partial_setup_script = []


            setup_path = os.path.join(
                root_directory, 'setup.py'
            )
            with open(setup_path) as setup:
                for line in setup.readlines():
                    if line.count('setup('):
                        break

                    partial_setup_script.append(
                        line
                    )

            tmp_locals = copy.copy(
                locals()
            )
            tmp_globals = copy.copy(
                globals()
            )

            tmp_globals['__file__'] = setup_path

            try:
                exec(
                    ''.join(partial_setup_script), tmp_globals, tmp_locals
                )
            except NameError:
                pass

            version_file = tmp_locals.get(
                '_version_file'
            ).name


            with open(version_file) as _version_file:
                version_file_data = _version_file.read()

            current_version = semantic_version.Version(re.match(
                r'.*__version__ = \'(.*?)\'', version_file_data, re.DOTALL
            ).group(1))

            new_version = copy.copy(
                current_version
            )

            with open(version_file, 'w') as _version_file:

                if version is None:
                    new_version.patch = 0
                    new_version.minor = 0
                    new_version.major +=1

                else:
                    new_version = semantic_version.Version(
                        version
                    )

                _version_file.write(
                    version_file_data.replace(str(current_version), str(new_version))
                )


            document_paths = list()
            for path, dirs, objs in os.walk(os.path.join(root_directory, 'doc')):
                for obj in objs:
                    if obj.lower() in ('release.rst', 'release_notes.rst', 'migration.rst'):
                        document_paths.append(
                            os.path.join(path, obj)
                        )

            difference = False
            for document_path in document_paths:
                new_doc_data = []
                with open(document_path) as doc_file:
                    for line in doc_file.readlines():
                        if line.lower().count('release::') and line.lower().count('upcoming'):
                            difference = True

                            line = line.lower().replace(
                                'upcoming', str(new_version)
                            )

                            new_doc_data.append(
                                line
                            )

                            new_doc_data.append(
                                '    :date: {0}'.format(
                                    datetime.datetime.now().strftime('%Y-%m-%d')
                                )
                            )

                            new_doc_data.append(
                                '\n'
                            )

                        else:
                            new_doc_data.append(line)


                with open(document_path, 'w') as doc_file:
                    doc_file.writelines(
                        new_doc_data
                    )

            if not difference:
                api.local(
                    'git tag -l'
                )

                logger.warning(
                    'No changes detected, aborting version at {0} -- {1}'.format(
                        current_version, checkout_directory
                    )
                )

                return

            api.local(
                'git status'
            )

            api.local(
                'git diff'
            )

            api.local(
                'git commit -a -m "automatic version update"'
            )

            api.local(
                'git tag -f {0}'.format(
                    str(new_version)
                )
            )

            #api.local(
            #    'python setup.py build_sphinx'
            #)



            if isinstance(push, str) and strtobool(push) or push:
                api.local(
                    'git push origin {0}'.format(
                        branch
                    )
                )

                api.local(
                    'git push origin {0}'.format(str(new_version))
                )

            logging.info(
                'updated version in : {0}'.format(
                    root_directory
                )
            )

