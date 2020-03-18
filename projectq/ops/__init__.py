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

import inspect
import pkgutil
from importlib import import_module

# Allow extending this namespace.
__path__ = pkgutil.extend_path(__path__, __name__)

from ._basics import (NotMergeable,
                      NotInvertible,
                      BasicGate,
                      MatrixGate,
                      SelfInverseGate,
                      BasicRotationGate,
                      ClassicalInstructionGate,
                      FastForwardingGate,
                      BasicMathGate,
                      BasicPhaseGate)


def dynamic_import(name):
    imported_module = import_module('.' + name, package=__name__)

    for attr_name in dir(imported_module):
        module_attr = getattr(imported_module, attr_name)

        # Only automatically import classes that derive from BasicGate or
        # Exception and that have not already been imported and avoid
        # importing classes from other ProjectQ submodules
        if (attr_name not in globals()
                and (inspect.isclass(module_attr)
                     and issubclass(module_attr, (BasicGate, Exception))
                     or isinstance(module_attr, BasicGate))
                and __name__ in module_attr.__module__):
            globals()[attr_name] = module_attr

        # If present, import all symbols from the 'all_defined_symbols' list
        if attr_name == 'all_defined_symbols':
            for symbol in module_attr:
                globals()[symbol.__name__] = symbol


_failed_list = []
for (_, pkg_name, _) in pkgutil.iter_modules(path=__path__):
    if pkg_name.endswith('test') or pkg_name == '_basics':
        continue
    try:
        dynamic_import(pkg_name)
    except ImportError:
        _failed_list.append(pkg_name)

for pkg_name in _failed_list:
    dynamic_import(pkg_name)
