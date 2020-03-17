import sys
from ._basics import BasicEngine, LastEngineException, ForwarderEngine

# Avoid dependency loop
setattr(sys.modules['projectq.cengines'], 'BasicEngine', BasicEngine)
setattr(sys.modules['projectq.cengines'], 'LastEngineException',
        LastEngineException)

from ._cmdmodifier import CommandModifier
from ._basicmapper import BasicMapperEngine
from ._swap_utils import return_swap_depth
from ._main import MainEngine, NotYetMeasuredError
