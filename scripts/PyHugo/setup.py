from setuptools import setup, Extension, find_packages
from setuptools.dist import Distribution
import setuptools.command.build_ext
import setuptools.command.install
import shutil, glob, os, sys

cwd = os.path.dirname(os.path.abspath(__file__))
go_path = os.path.join(cwd, "go")

# Heavily inspired by PyTorch setup.py

class clean(setuptools.Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import glob

        with open('.gitignore', 'r') as f:
            ignores = f.read()
            for wildcard in filter(None, ignores.split('\n')):
                wildcard = wildcard.lstrip('./')
                for filename in glob.glob(wildcard):
                    try:
                        os.remove(filename)
                    except OSError:
                        shutil.rmtree(filename, ignore_errors=True)

def main():
    dist = Distribution()
    dist.script_name = os.path.basename(sys.argv[0])
    dist.script_args = sys.argv[1:]
    try:
        dist.parse_command_line()
    except setuptools.distutils.errors.DistutilsArgError as e:
        print(e)
        sys.exit(1)

    cmdclass = {
        'clean': clean,
    }

    hugolib = Extension('PyHugolib.hugolib',
                    sources = ['go/hugolib.go'])

    setup(name="PyHugolib",
        version="0.0.1",
        description="Python interface for Hugolib",
        author="Christian Mahnke",
        author_email="cmahnke@gmail.com",
        cmdclass=cmdclass,
        packages=setuptools.find_packages(),
        ext_modules=[hugolib],
        build_golang={'root': 'projektemacher.org/hugo/python'},
        setup_requires=[
            'setuptools-golang>=2.7.0'
        ])

if __name__ == "__main__":
    main()
