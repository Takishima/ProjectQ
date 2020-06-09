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
# Parts of the code are copied from:
# tools/pybind11Tools.cmake -- Build system for the pybind11 modules
#
# Copyright (c) 2015 Wenzel Jakob <wenzel@inf.ethz.ch>
#
# All rights reserved. Use of this source code is governed by a
# BSD-style license that can be found in the LICENSE file.
# ==============================================================================

execute_process(
  COMMAND
    "${Python3_EXECUTABLE}" "-c"
    "from distutils import sysconfig as s;import sys;import struct;
print(s.get_config_var('SO'));
"
  OUTPUT_STRIP_TRAILING_WHITESPACE
  RESULT_VARIABLE _PYTHON_SUCCESS
  OUTPUT_VARIABLE Python3_MODULE_EXTENSION
  ERROR_VARIABLE _PYTHON_ERROR_VALUE)

set(_python_targets)

# ==============================================================================

# Checks whether the given CXX/linker flags can compile and link a cxx file.
# cxxflags and linkerflags are lists of flags to use.  The result variable is
# a unique variable name for each set of flags: the compilation result will be
# cached base on the result variable.  If the flags work, sets them in
# cxxflags_out/linkerflags_out internal cache variables (in addition to
# ${result}).
function(_return_if_cxx_and_linker_flags_work result cxxflags linkerflags
         cxxflags_out linkerflags_out)
  set(CMAKE_REQUIRED_LIBRARIES ${linkerflags})
  check_cxx_compiler_flag("${cxxflags}" ${result})
  if(${result})
    set(${cxxflags_out}
        "${cxxflags}"
        CACHE INTERNAL "" FORCE)
    set(${linkerflags_out}
        "${linkerflags}"
        CACHE INTERNAL "" FORCE)
  endif()
endfunction()

# Internal: find the appropriate link time optimization flags for this
#           compiler
function(_add_lto_flags target_name prefer_thin_lto)
  if(NOT DEFINED PYBIND11_LTO_CXX_FLAGS)
    set(PYBIND11_LTO_CXX_FLAGS
        ""
        CACHE INTERNAL "")
    set(PYBIND11_LTO_LINKER_FLAGS
        ""
        CACHE INTERNAL "")

    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
      set(cxx_append "")
      set(linker_append "")
      if(CMAKE_CXX_COMPILER_ID MATCHES "Clang" AND NOT APPLE)
        # Clang Gold plugin does not support -Os; append -O3 to MinSizeRel
        # builds to override it
        set(linker_append ";$<$<CONFIG:MinSizeRel>:-O3>")
      elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU")
        set(cxx_append ";-fno-fat-lto-objects")
      endif()

      if(CMAKE_CXX_COMPILER_ID MATCHES "Clang" AND prefer_thin_lto)
        _return_if_cxx_and_linker_flags_work(
          HAS_FLTO_THIN "-flto=thin${cxx_append}" "-flto=thin${linker_append}"
          PYBIND11_LTO_CXX_FLAGS PYBIND11_LTO_LINKER_FLAGS)
      endif()

      if(NOT HAS_FLTO_THIN)
        _return_if_cxx_and_linker_flags_work(
          HAS_FLTO "-flto${cxx_append}" "-flto${linker_append}"
          PYBIND11_LTO_CXX_FLAGS PYBIND11_LTO_LINKER_FLAGS)
      endif()
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "Intel")
      # Intel equivalent to LTO is called IPO
      _return_if_cxx_and_linker_flags_work(
        HAS_INTEL_IPO "-ipo" "-ipo" PYBIND11_LTO_CXX_FLAGS
        PYBIND11_LTO_LINKER_FLAGS)
    elseif(MSVC)
      # cmake only interprets libraries as linker flags when they start with a
      # - (otherwise it converts /LTCG to \LTCG as if it was a Windows path).
      # Luckily MSVC supports passing flags with - instead of /, even if it is
      # a bit non-standard:
      _return_if_cxx_and_linker_flags_work(
        HAS_MSVC_GL_LTCG "/GL" "-LTCG" PYBIND11_LTO_CXX_FLAGS
        PYBIND11_LTO_LINKER_FLAGS)
    endif()

    if(PYBIND11_LTO_CXX_FLAGS)
      message(STATUS "LTO enabled")
    else()
      message(
        STATUS "LTO disabled (not supported by the compiler and/or linker)")
    endif()
  endif()

  # Enable LTO flags if found, except for Debug builds
  if(PYBIND11_LTO_CXX_FLAGS)
    target_compile_options(
      ${target_name}
      PRIVATE "$<$<NOT:$<CONFIG:Debug>>:${PYBIND11_LTO_CXX_FLAGS}>")
  endif()
  if(PYBIND11_LTO_LINKER_FLAGS)
    target_link_libraries(
      ${target_name}
      PRIVATE "$<$<NOT:$<CONFIG:Debug>>:${PYBIND11_LTO_LINKER_FLAGS}>")
  endif()
endfunction()

# ------------------------------------------------------------------------------

function(add_python_module target_name)
  cmake_parse_arguments(ARG "MODULE;SHARED;SYSTEM;THIN_LTO" "" "" ${ARGN})

  if(ARG_MODULE AND ARG_SHARED)
    message(FATAL_ERROR "Cannot be both MODULE and SHARED")
  elseif(ARG_SHARED)
    set(lib_type SHARED)
  else()
    set(lib_type MODULE)
  endif()

  add_library(${target_name} ${lib_type} ${ARG_UNPARSED_ARGUMENTS})

  if(ARG_SYSTEM)
    set(inc_isystem SYSTEM)
  endif()

  set(PYBIND11_INCLUDE_DIRS)
  separate_arguments(_tmp NATIVE_COMMAND ${PYBIND11_INCLUDE_DIR})
  foreach(_inc_arg ${_tmp})
    string(REGEX REPLACE "^[-/]I" "" _inc_arg ${_inc_arg})
    list(APPEND PYBIND11_INCLUDE_DIRS ${_inc_arg})
  endforeach()

  target_include_directories(
    ${target_name} ${inc_isystem}
    PRIVATE ${PYBIND11_INCLUDE_DIRS}
    PRIVATE ${Python3_INCLUDE_DIRS})

  set_target_properties(
    ${target_name}
    PROPERTIES PREFIX "${Python3_MODULE_PREFIX}" SUFFIX
                                                 "${Python3_MODULE_EXTENSION}"
               CXX_VISIBILITY_PRESET "hidden")

  if(WIN32 OR CYGWIN)
    # Link against the Python shared library on Windows
    target_link_libraries(${target_name} PRIVATE ${Python3_LIBRARIES})
  elseif(APPLE)
    target_link_libraries(${target_name} PRIVATE "-undefined dynamic_lookup")

    if(ARG_SHARED)
      set_target_properties(${target_name} PROPERTIES MACOSX_RPATH ON)
    endif()
  endif()

  _add_lto_flags(${target_name} ${ARG_THIN_LTO})

  if(NOT MSVC AND NOT ${CMAKE_BUILD_TYPE} MATCHES Debug|RelWithDebInfo)
    # Strip unnecessary sections of the binary on Linux/Mac OS
    if(CMAKE_STRIP)
      if(APPLE)
        add_custom_command(
          TARGET ${target_name}
          POST_BUILD
          COMMAND ${CMAKE_STRIP} -x $<TARGET_FILE:${target_name}>)
      else()
        add_custom_command(
          TARGET ${target_name}
          POST_BUILD
          COMMAND ${CMAKE_STRIP} $<TARGET_FILE:${target_name}>)
      endif()
    endif()
  endif()

  if(MSVC)
    # /MP enables multithreaded builds (relevant when there are many files), /bigobj is
    # needed for bigger binding projects due to the limit to 64k addressable sections
    target_compile_options(${target_name} PRIVATE /bigobj)
    if(CMAKE_VERSION VERSION_LESS 3.11)
      target_compile_options(${target_name}
                             PRIVATE $<$<NOT:$<CONFIG:Debug>>:/MP>)
    else()
      # Only set these options for C++ files.  This is important so that, for
      # instance, projects that include other types of source files like CUDA
      # .cu files don't get these options propagated to nvcc since that would
      # cause the build to fail.
      target_compile_options(
        ${target_name}
        PRIVATE $<$<NOT:$<CONFIG:Debug>>:$<$<COMPILE_LANGUAGE:CXX>:/MP>>)
    endif()
  endif()

  list(APPEND _doc_targets ${target_name})
  set(_doc_targets
      ${_doc_targets}
      PARENT_SCOPE)
  list(APPEND _python_targets ${target_name})
  set(_python_targets
      ${_python_targets}
      PARENT_SCOPE)

  string(TOUPPER ${target_name} _TARGET_NAME)

  if(${target_name}_LIBRARY_OUTPUT_DIRECTORY)
    set(${_TARGET_NAME}_LIBRARY_OUTPUT_DIRECTORY
        ${${target_name}_LIBRARY_OUTPUT_DIRECTORY})
  endif()

  # Properly set output directory for a target so that during an installation
  # using either 'pip install' or 'python3 setup.py install' the libraries get
  # built in the proper directory
  if(${_TARGET_NAME}_LIBRARY_OUTPUT_DIRECTORY)
    set_target_properties(
      ${target_name}
      PROPERTIES LIBRARY_OUTPUT_DIRECTORY
                 ${${_TARGET_NAME}_LIBRARY_OUTPUT_DIRECTORY}
                 LIBRARY_OUTPUT_DIRECTORY_DEBUG
                 ${${_TARGET_NAME}_LIBRARY_OUTPUT_DIRECTORY}
                 LIBRARY_OUTPUT_DIRECTORY_RELEASE
                 ${${_TARGET_NAME}_LIBRARY_OUTPUT_DIRECTORY}
                 LIBRARY_OUTPUT_DIRECTORY_RELWITHDEBINFO
                 ${${_TARGET_NAME}_LIBRARY_OUTPUT_DIRECTORY}
                 LIBRARY_OUTPUT_DIRECTORY_MINSIZEREL
                 ${${_TARGET_NAME}_LIBRARY_OUTPUT_DIRECTORY})
  elseif(IS_PYTHON_BUILD)
    message(
      WARNING "IS_PYTHON_BUILD=ON but ${_TARGET_NAME}_LIBRARY_OUTPUT_DIRECTORY "
              "was not defined! The shared library for target ${target_name} "
              "will probably not be copied to the correct directory.")
  endif(${_TARGET_NAME}_LIBRARY_OUTPUT_DIRECTORY)

endfunction()
