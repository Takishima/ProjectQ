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

from ._core import (BasicEngine, LastEngineException, ForwarderEngine,
                    BasicEngine, LastEngineException, CommandModifier,
                    BasicMapperEngine, MainEngine, NotYetMeasuredError,
                    return_swap_depth)


def dynamic_import(name):
    imported_module = import_module('.' + name, package=__name__)

    for attr_name in dir(imported_module):
        module_attr = getattr(imported_module, attr_name)

        # Only automatically import classes that derive from BasicEngine or
        # Exception and that have not already been imported and avoid
        # importing classes from other ProjectQ submodules
        if (inspect.isclass(module_attr)
                and issubclass(module_attr, (BasicEngine, Exception))
                and attr_name not in globals()
                and __name__ in module_attr.__module__):
            globals()[attr_name] = module_attr

        # If present, import all symbols from the 'all_defined_symbols' list
        if attr_name == 'all_defined_symbols':
            for symbol in module_attr:
                globals()[symbol.__name__] = symbol


# Allow extending this namespace.
__path__ = pkgutil.extend_path(__path__, __name__)

_failed_list = []
for (_, name, _) in pkgutil.iter_modules(path=__path__):
    if name.endswith('test') or name == '_core':
        continue
    try:
        dynamic_import(name)
    except ImportError:
        _failed_list.append(name)

for name in _failed_list:
    dynamic_import(name)
