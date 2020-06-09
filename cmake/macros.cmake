# ==============================================================================
#
# Copyright 2020 <Huawei Technologies Co., Ltd>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ==============================================================================

include(CheckCXXCompilerFlag)

# Find a compatible compiler flag from a series of list of possible flags
# For each list of whitespace separated compiler flags passed in argument, this
# function will append or save the compatible flags in ${var_prefix}_cxx
macro(check_compiler_flags var_prefix)
  set(_cxx_opts)

  foreach(_flag_list ${ARGN})
    separate_arguments(_flag_list)

    foreach(_flag ${_flag_list})
      # Drop the first character (most likely either '-' or '/')
      string(SUBSTRING ${_flag} 1 -1 _flag_name)
      string(REGEX REPLACE "[-:/]" "_" _flag_name ${_flag_name})

      check_cxx_compiler_flag(${_flag} cxx_compiler_has_${_flag_name})
      if(cxx_compiler_has_${_flag_name})
        list(APPEND _cxx_opts ${_flag})
        break()
      endif()
    endforeach()
  endforeach()

  if(DEFINED ${var_prefix}_cxx)
    list(APPEND ${var_prefix}_cxx ${_cxx_opts})
  else()
    set(${var_prefix}_cxx ${_cxx_opts})
  endif()
endmacro()

# ==============================================================================

macro(define_target namespace comp incpath)
  string(TOUPPER ${comp} uppercomponent)
  add_library(${namespace}::${comp} UNKNOWN IMPORTED)
  if(incpath)
    set_target_properties(${namespace}::${COMPONENT}
                          PROPERTIES INTERFACE_INCLUDE_DIRECTORIES "${incpath}")
  endif()
  if(EXISTS "${${namespace}_${uppercomponent}_LIBRARY}")
    set_target_properties(
      ${namespace}::${comp}
      PROPERTIES IMPORTED_LINK_INTERFACE_LANGUAGES "CXX"
                 IMPORTED_LOCATION "${${namespace}_${uppercomponent}_LIBRARY}")
  endif()
  if(EXISTS "${${namespace}_${uppercomponent}_LIBRARY_RELEASE}")
    set_property(
      TARGET ${namespace}::${comp}
      APPEND
      PROPERTY IMPORTED_CONFIGURATIONS RELEASE)
    set_target_properties(
      ${namespace}::${comp}
      PROPERTIES IMPORTED_LINK_INTERFACE_LANGUAGES_RELEASE "CXX"
                 IMPORTED_LOCATION_RELEASE
                 "${${namespace}_${uppercomponent}_LIBRARY_RELEASE}")
  endif()
  if(EXISTS "${${namespace}_${uppercomponent}_LIBRARY_DEBUG}")
    set_property(TARGET ${namespace}::${comp} APPEND
                 PROPERTY IMPORTED_CONFIGURATIONS DEBUG)
    set_target_properties(
      ${namespace}::${comp}
      PROPERTIES IMPORTED_LINK_INTERFACE_LANGUAGES_DEBUG "CXX"
                 IMPORTED_LOCATION_DEBUG
                 "${${namespace}_${uppercomponent}_LIBRARY_DEBUG}")
  endif()
  message(STATUS "${comp} | ${${namespace}_${uppercomponent}_DEPENDENCIES}")
  if(${namespace}_${uppercomponent}_DEPENDENCIES)
    unset(${namespace}_${uppercomponent}_TARGET_DEPENDENCIES)
    foreach(dep ${${namespace}_${uppercomponent}_DEPENDENCIES})
      list(APPEND ${namespace}_${uppercomponent}_TARGET_DEPENDENCIES
           Boost::${dep})
    endforeach()
    if(COMPONENT STREQUAL "thread")
      list(APPEND ${namespace}_${uppercomponent}_TARGET_DEPENDENCIES
           Threads::Threads)
    endif()
    set_target_properties(
      ${namespace}::${comp}
      PROPERTIES INTERFACE_LINK_LIBRARIES
                 "${${namespace}_${uppercomponent}_TARGET_DEPENDENCIES}")
  endif()
endmacro(define_target)

# ==============================================================================

function(find_python_module module)
  cmake_parse_arguments(PARSE_ARGV 1 PYMOD "REQUIRED;EXACT" "VERSION" "")

  string(TOUPPER ${module} MODULE)
  if(NOT PYMOD_${MODULE})
    if(PYMOD_REQUIRED)
      set(PYMOD_${MODULE}_FIND_REQUIRED TRUE)
    endif()
    if(PYMOD_EXACT)
      set(PYMOD_${MODULE}_FIND_VERSION_EXACT TRUE)
    endif()
    if(PYMOD_VERSION)
      set(PYMOD_${MODULE}_FIND_VERSION ${PYMOD_VERSION})
    endif()

    execute_process(
      COMMAND "${Python3_EXECUTABLE}" "-c"
              "import os, ${module}; print(os.path.dirname(${module}.__file__))"
      RESULT_VARIABLE _${MODULE}_status
      OUTPUT_VARIABLE _${MODULE}_location
      ERROR_QUIET OUTPUT_STRIP_TRAILING_WHITESPACE)

    if(NOT _${MODULE}_status)
      set(PYMOD_${MODULE}
          ${_${MODULE}_location}
          CACHE STRING "Location of Python module ${module}")

      if(PYMOD_VERSION)
        execute_process(
          COMMAND "${Python3_EXECUTABLE}" "-c"
                  "import ${module}; print(${module}.__version__)"
          RESULT_VARIABLE _${MODULE}_status
          OUTPUT_VARIABLE _${MODULE}_version ERROR_QUIET
                          OUTPUT_STRIP_TRAILING_WHITESPACE)

        if(NOT _${MODULE}_status)
          set(PYMOD_${MODULE}_VERSION
              ${_${MODULE}_version}
              CACHE STRING "Version of Python module ${module}")
        endif()
      endif()
    endif()
  endif()

  find_package_handle_standard_args(
    PYMOD_${MODULE}
    REQUIRED_VARS PYMOD_${MODULE}
    VERSION_VAR PYMOD_${MODULE}_VERSION)

  mark_as_advanced(PYMOD_${MODULE} PYMOD_${MODULE}_VERSION)
endfunction()

# ==============================================================================
