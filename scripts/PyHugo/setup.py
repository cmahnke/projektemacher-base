from distutils.core import setup, Extension
import setuptools

class build_ext(setuptools.command.build_ext.build_ext):
    pass

def build_deps():
    pass

def main():
    hugolib = Extension('hugolib',
                    define_macros = [('MAJOR_VERSION', '1'),
                                     ('MINOR_VERSION', '0')],
                    include_dirs = ['/usr/local/include'],
                    libraries = ['tcl83'],
                    library_dirs = ['/usr/local/lib'],
                    sources = ['hugolib.go'])

    setup(name="PyHugolib",
        version="0.0.1",
        description="Python interface for Hugolib",
        author="Christian Mahnke",
        author_email="cmahnke@gmail.com",
        packages=setuptools.find_packages(),
        ext_modules=[hugolib],
        setup_requires=[
            'setuptools-golang>=1.1.0'
        ])

if __name__ == "__main__":
    main()
