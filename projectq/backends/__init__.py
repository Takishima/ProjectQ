#   Copyright 2017 ProjectQ-Framework (www.projectq.ch)
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
"""
Contains back-ends for ProjectQ.

This includes:

* a debugging tool to print all received commands (CommandPrinter)
* a circuit drawing engine (which can be used anywhere within the compilation
  chain)
* a simulator with emulation capabilities
* a resource counter (counts gates and keeps track of the maximal width of the
  circuit)
* an interface to the IBM Quantum Experience chip (and simulator).
"""
import sys
import inspect
import pkgutil
from importlib import import_module

# Allow extending this namespace.
__path__ = __import__('pkgutil').extend_path(__path__, __name__)

from projectq.cengines import BasicEngine


def dynamic_import(name):
    imported_module = import_module('.' + name, package=__name__)

    for attr_name in dir(imported_module):
        module_attr = getattr(imported_module, attr_name)

        # Only automatically import classes that derive from BasicEngine and
        # that have not already been imported and avoid importing classes from
        # other ProjectQ submodules
        if (inspect.isclass(module_attr)
                and issubclass(module_attr, BasicEngine)
                and attr_name not in globals()
                and __name__ in module_attr.__module__):
            globals()[attr_name] = module_attr


_failed_list = []
for (_, pkg_name, _) in pkgutil.iter_modules(path=__path__):
    if pkg_name.endswith('test'):
        continue
    try:
        dynamic_import(pkg_name)
    except ImportError:
        _failed_list.append(pkg_name)

for pkg_name in _failed_list:
    dynamic_import(pkg_name)
