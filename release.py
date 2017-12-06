from tempfile import mkstemp
from shutil import move
import subprocess
from os import fdopen, remove

import pypandoc

from geomeppy import __version__


def replace(file_path, pattern, subst):
    # Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    # Remove original file
    remove(file_path)
    # Move new file
    move(abs_path, file_path)


def main():
    # check we're on master
    assert b'* master' in subprocess.check_output(['git', 'branch']), 'Not on master branch'
    # check we're up-to-date
    status = subprocess.check_output(['git', 'status'])
    assert b'modified' not in status, 'Repository contains modified files'
    assert b'Untracked' not in status, 'Repository contains untracked files'

    # increment version
    version = __version__
    major, minor, patch = version.split('.')
    new_version = '%s.%s.%d' % (major, minor, int(patch) + 1)
    replace('geomeppy/__init__.py', version, new_version)
    replace('setup.py', version, new_version)
    try:
        # convert docs to rst
        z = pypandoc.convert('README.md', 'rst', format='markdown')
        with open('README.rst', 'w') as outfile:
            outfile.write(z)
        # add and commit changes
        print(subprocess.check_output(['git', 'add', 'geomeppy/__init__.py']))
        print(subprocess.check_output(['git', 'add', 'setup.py']))
        print(subprocess.check_output(['git', 'add', 'README.rst']))
        print(subprocess.check_output(['git', 'commit', '-m', 'release/%s' % new_version]))
        # create a tagged release
        print(subprocess.check_output(['git', 'tag', '-m', 'release/%s' % new_version, 'v%s' % new_version]))
        # push to github
        print(subprocess.check_output(['git', 'push', 'origin', 'master', '-f']))
        # create dist
        print(subprocess.check_output(['python', 'setup.py', 'sdist']))
        # release
        print(subprocess.check_output(['twine', 'upload', 'dist/*']))
    except Exception as e:
        # rollback
        print('rolling back')
        print(e)
        replace('geomeppy/__init__.py', new_version, version)
        replace('setup.py', new_version, version)


if __name__ == '__main__':
    main()
