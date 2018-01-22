from os import fdopen, remove
from shutil import move
import subprocess
import sys
from tempfile import mkstemp

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


def main(increment):
    # check we're on develop
    assert b'* develop' in subprocess.check_output(['git', 'branch']), 'Not on develop branch'
    # check we're up-to-date
    status = subprocess.check_output(['git', 'status'])
    assert b'modified' not in status, 'Repository contains modified files'
    assert b'Untracked' not in status, 'Repository contains untracked files'

    # increment version
    version = __version__
    new_version = [int(i) for i in version.split('.')]
    for i in range(len(new_version)):
        if i == increment:
            new_version[i] += 1
        if i > increment:
            new_version[i] = 1

    new_version = '.'.join(str(v) for v in new_version)
    replace('geomeppy/__init__.py', version, new_version)
    replace('setup.py', "version='%s'" % version, "version='%s'" % new_version)
    replace('setup.py', "tarball/v%s" % version, "tarball/v%s" % new_version)
    replace('docs/source/conf.py',
            "version = '%s'" % '.'.join(version.split('.')[:-1]),
            "version = '%s'" % '.'.join(new_version.split('.')[:-1])
            )
    replace('docs/source/conf.py', "release = '%s'" % version, "release = '%s'" % new_version)

    try:
        # add and commit changes
        print(subprocess.check_output(['git', 'add', 'geomeppy/__init__.py']))
        print(subprocess.check_output(['git', 'add', 'setup.py']))
        print(subprocess.check_output(['git', 'add', 'docs/source/conf.py']))
        print(subprocess.check_output(['git', 'add', 'README.rst']))
        print(subprocess.check_output(['git', 'commit', '-m', 'release/%s' % new_version]))
    except Exception as e:
        # rollback
        print('rolling back')
        print(e)
        replace('geomeppy/__init__.py', new_version, version)
        replace('setup.py', new_version, version)
        exit()
    try:
        # push the changes
        print(subprocess.check_output(['git', 'push', 'origin', 'develop', '-f']))
        # create a tagged release
        print(subprocess.check_output(['git', 'tag', 'release/%s' % new_version, '-m', 'v%s' % new_version]))
        # push to github
        print(subprocess.check_output(['git', 'push', 'origin', 'release/%s' % new_version, '-f']))
    except Exception as e:
        # rollback
        print('rolling back tag')
        print(e)
        # delete the tagged release
        print(subprocess.check_output(['git', 'tag', '-d', 'release/%s' % new_version, 'v%s' % new_version]))
        # push to github
        print(subprocess.check_output(
            ['git', 'push', 'origin', ':refs/tags/release/%s' % new_version, 'v%s' % new_version])
        )
    # from here, the Travis CI magic begins


if __name__ == '__main__':
    args = sys.argv[1:]
    VERSION = ['major', 'minor', 'patch']
    try:
        increment = VERSION.index(sys.argv[1])
    except ValueError:
        print('%s is not a valid semantic version level (use major, minor, or patch)' % sys.argv[1])
    except IndexError:
        # default
        increment = VERSION.index('patch')

    main(increment)
