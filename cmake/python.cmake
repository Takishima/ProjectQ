find_package(Python3 REQUIRED COMPONENTS Interpreter)
find_python_module(pip REQUIRED)
find_python_module(pybind11 REQUIRED)
execute_process(COMMAND "${Python3_EXECUTABLE}" "-m" "pybind11" "--include"
                RESULT_VARIABLE PYBIND11_INCLUDE_DIR)

execute_process(
  COMMAND
    "${Python3_EXECUTABLE}" "-c"
    "from distutils import sysconfig as s;import sys;import struct;
print(s.get_config_var('SO'));
print(hasattr(sys, 'gettotalrefcount')+0);
print(struct.calcsize('@P'));
print(s.get_config_var('LDVERSION') or s.get_config_var('VERSION'));
print(s.get_config_var('LIBDIR') or '');
print(s.get_config_var('MULTIARCH') or '');
"
  RESULT_VARIABLE _PYTHON_SUCCESS
  OUTPUT_VARIABLE _PYTHON_VALUES
  ERROR_VARIABLE _PYTHON_ERROR_VALUE)
