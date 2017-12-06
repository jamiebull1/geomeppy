from tempfile import mkstemp
from shutil import move
import subprocess
from os import fdopen, remove

import pypandoc

import geomeppy


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
    assert b'* master' in subprocess.check_output(['git', 'branch'])
    # check we're up-to-date
    status = subprocess.check_output(['git', 'status'])
    assert b'modified' not in status
    assert b'Untracked' not in status

    # increment version
    version = geomeppy.__version__
    major, minor, patch = version.split('.')
    new_version = '%s.%s.%d' % (major, minor, int(patch) + 1)
    replace('geomeppy/__init__.py', version, new_version)
    try:
        # convert docs to rst
        z = pypandoc.convert('README.md', 'rst', format='markdown')
        with open('README.rst', 'w') as outfile:
            outfile.write(z)
        # add and commit changes
        subprocess.check_call(['git', 'add', 'geomeppy/__init__.py'])
        subprocess.check_call(['git', 'add', 'README.rst'])
        # create a tagged release
        subprocess.check_call(['git', 'tag', '-m', 'Release %s' % new_version, 'v%s' % new_version])

        # TODO: push to github
        subprocess.check_call(['git', 'push', 'origin', 'master'])
        # create dist
        # subprocess.call(['python', 'setup.py', 'sdist'])
        # release
        # subprocess.call(['twine' 'upload' 'dist/*'])
    except Exception as e:
        # rollback
        print('rolling back')
        print(e)
        replace('geomeppy/__init__.py', new_version, version)


if __name__ == '__main__':
    main()
