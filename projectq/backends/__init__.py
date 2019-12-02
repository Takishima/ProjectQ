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
import os
import sys
import inspect
import pkgutil
from importlib import import_module

import projectq.cengines as cengines

for (_, name, _) in pkgutil.iter_modules([os.path.dirname(__file__)]):
    if name.endswith('test'):
        continue

    imported_module = import_module('.' + name, package=__name__)
    for i in dir(imported_module):
        attribute = getattr(imported_module, i)
        if (inspect.isclass(attribute)
                and issubclass(attribute, cengines.BasicEngine)
                and not hasattr(sys.modules[__name__], i)
                and __name__ in attribute.__module__):
            setattr(sys.modules[__name__], i, attribute)

# Allow extending this namespace.
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
