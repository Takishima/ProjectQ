#   Copyright 2020 <Huawei Technologies Co., Ltd>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os
import setuptools

import itertools
import os
import platform
import re
import subprocess
import sys

from distutils.command.clean import clean
from distutils.version import LooseVersion
import setuptools
from setuptools.command.build_ext import build_ext

# This reads the __version__ variable from _version.py
from projectq._version import __version__

# ==============================================================================


def get_python_executable():
    try:
        root_path = os.environ['VIRTUAL_ENV']
        python = os.path.basename(sys.executable)
        python_path = os.path.join(root_path, python)
        if os.path.exists(python_path):
            return python_path
        return os.path.join(root_path, 'bin', python)
    except KeyError:
        return sys.executable


def get_cmake_command():
    with open(os.devnull, 'w') as devnull:
        try:
            subprocess.check_call(['cmake', '--version'],
                                  stdout=devnull,
                                  stderr=devnull)
            return ['cmake']
        except (OSError, subprocess.CalledProcessError):
            pass

        # CMake not in PATH, should have installed Python CMake module
        # -> try to find out where it is
        try:
            root_path = os.environ['VIRTUAL_ENV']
            python = os.path.basename(sys.executable)
        except KeyError:
            root_path, python = os.path.split(sys.executable)

        search_paths = [
            root_path,
            os.path.join(root_path, 'bin'),
            os.path.join(root_path, 'Scripts')
        ]

        # First try executing CMake directly
        for base_path in search_paths:
            try:
                cmake_cmd = os.path.join(base_path, 'cmake')
                subprocess.check_call([cmake_cmd, '--version'],
                                      stdout=devnull,
                                      stderr=devnull)
                return [cmake_cmd]
            except (OSError, subprocess.CalledProcessError):
                pass

        # That did not work: try calling it through Python
        for base_path in search_paths:
            try:
                cmake_cmd = [python, os.path.join(base_path, 'cmake')]
                subprocess.check_call(cmake_cmd + ['--version'],
                                      stdout=devnull,
                                      stderr=devnull)
                return cmake_cmd
            except (OSError, subprocess.CalledProcessError):
                pass

    # Nothing worked -> give up!
    return None


# ------------------------------------------------------------------------------


def get_install_requires():
    requirements_file = 'requirements.txt'

    # Read in requirements.txt
    with open(requirements_file, 'r') as f_requirements:
        requirements = f_requirements.readlines()
    requirements = [r.strip() for r in requirements]

    # Add CMake as dependency if we cannot find the command
    if get_cmake_command() is None:
        requirements.append('cmake')

    return requirements


# ==============================================================================


class CMakeExtension(setuptools.Extension):
    def __init__(self, pymod, target=None):
        """
        Constructor

        Args:
            src_dir (string): Path to source directory
            target (string): Name of target
            pymod (string): Name of compiled Python module
        """
        # NB: the main source directory is the one containing the setup.py file
        self.src_dir = os.path.abspath('')
        self.pymod = pymod
        self.target = target if target is not None else pymod.split('.')[-1]

        self.lib_filepath = os.path.join(*pymod.split('.'))
        setuptools.Extension.__init__(self, pymod, sources=[])


# ------------------------------------------------------------------------------


class CMakeBuild(build_ext):
    def build_extensions(self):
        self.cmake_cmd = get_cmake_command()
        assert self.cmake_cmd is not None
        print('using cmake command:', *self.cmake_cmd)
        out = subprocess.check_output([*self.cmake_cmd, '--version'])

        if platform.system() == "Windows":
            cmake_version = LooseVersion(
                re.search(r'version\s*([\d.]+)', out.decode()).group(1))
            if cmake_version < '3.1.0':
                raise RuntimeError("CMake >= 3.1.0 is required on Windows")

        self.parallel = 2
        self.configure_extensions()
        build_ext.build_extensions(self)

    def configure_extensions(self):
        def _src_dir_pred(ext):
            return ext.src_dir

        cmake_args = [
            '-DPython3_EXECUTABLE=' + get_python_executable(),
            '-DIS_PYTHON_BUILD:BOOL=ON',
            '-DCMAKE_VERBOSE_MAKEFILE:BOOL=ON'
        ]  # yapf: disable

        cfg = 'Debug' if self.debug else 'Release'
        self.build_args = ['--config', cfg]

        if platform.system() == "Windows":
            if sys.maxsize > 2**32:
                cmake_args += ['-A', 'x64']
            self.build_args += ['--', '/m']
        else:
            cmake_args += ['-DCMAKE_BUILD_TYPE=' + cfg]
            self.build_args += ['--', '-j2']

        env = os.environ.copy()
        env['CXXFLAGS'] = '{} -DVERSION_INFO=\\"{}\\"'.format(
            env.get('CXXFLAGS', ''), self.distribution.get_version())

        # This can in principle handle the compilation of extensions outside
        # the main CMake directory (ie. outside the one containing this
        # setup.py file)
        for src_dir, extensions in itertools.groupby(sorted(self.extensions,
                                                            key=_src_dir_pred),
                                                     key=_src_dir_pred):
            self.cmake_configure_build(src_dir, extensions, cmake_args, env)

    def cmake_configure_build(self, src_dir, extensions, cmake_args, env):
        args = cmake_args.copy()
        for ext in extensions:
            dest_path = os.path.abspath(
                os.path.dirname(self.get_ext_fullpath(ext.lib_filepath)))
            args.append('-D{}_LIBRARY_OUTPUT_DIRECTORY={}'.format(
                ext.target.upper(), dest_path))

        build_temp = self._get_temp_dir(src_dir)
        if not os.path.exists(build_temp):
            os.makedirs(build_temp)

        subprocess.check_call(self.cmake_cmd + [src_dir] + args,
                              cwd=build_temp,
                              env=env)

    def build_extension(self, ext):
        subprocess.check_call(self.cmake_cmd
                              + ['--build', '.', '--target', ext.target]
                              + self.build_args,
                              cwd=self._get_temp_dir(ext.src_dir))

    def _get_temp_dir(self, src_dir):
        return os.path.join(self.build_temp, os.path.basename(src_dir))


# ==============================================================================


class Clean(clean):
    def run(self):
        # Execute the classic clean command
        clean.run(self)
        import glob
        from distutils.dir_util import remove_tree
        egg_info = glob.glob('pysrc/*.egg-info')
        if egg_info:
            remove_tree(egg_info[0])


# ==============================================================================

# This package's name
pkg_name = 'hiq-projectq'

# This reads the __version__ variable from projectq/_version.py
exec(open('projectq/_version.py').read())

# Readme file as long_description:
long_description = open('README.rst').read()

long_description += open('CHANGELOG.rst').read()

# ------------------------------------------------------------------------------

ext_modules = [
    CMakeExtension(pymod='projectq.backends._sim._cppsim'),
]

# ==============================================================================

def run():
    setuptools.setup(
        name='ProjectQ',
        version=__version__,
        author='HiQ',
        author_email='hiqinfo@huawei.com',
        url='http://www.projectq.ch',
        project_urls={
            'Documentation': 'https://projectq.readthedocs.io/en/latest/',
            'Issue Tracker': 'https://github.com/ProjectQ-Framework/ProjectQ/',
        },
        description=('ProjectQ - An open source software framework for '
                     'quantum computing'),
        long_description=long_description,
        install_requires=get_install_requires(),
        cmdclass=dict(build_ext=CMakeBuild, clean=Clean),
        zip_safe=False,
        license='Apache 2',
        packages=setuptools.find_packages(),
        ext_modules=ext_modules)
