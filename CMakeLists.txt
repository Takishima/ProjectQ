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

cmake_minimum_required(VERSION 3.13)

set(_policy_list
    CMP0012
    CMP0023
    CMP0028
    CMP0042
    CMP0048
    CMP0051
    CMP0054
    CMP0057
    CMP0074
    CMP0076
    CMP0079)
foreach(_policy ${_policy_list})
  if(POLICY ${_policy})
    cmake_policy(SET ${_policy} NEW)
  endif()
  # CMP0012: if() recognizes numbers and booleans
  # CMP0028: :: in target names
  # CMP0042: MACOS_RPATH
  # CMP0048: allow VERSION in project()
  # CMP0051: list TARGET_OBJECTS in SOURCES property
  # CMP0054: no more de-referencing of "expr" in if() statements
  # CMP0057: if IN_LIST
  # CMP0074: XXX_ROOT variables for find_package(XXX)
  # CMP0076: target_sources relative paths
  # CMP0079: target_link_libraries allows use with targets in other directories
  #          (CMake 3.13 minimum)
endforeach()

# ==============================================================================
# Macro definitions

include(${CMAKE_CURRENT_LIST_DIR}/cmake/macros.cmake)

# ==============================================================================
# Create the ProjectQ-CXX project

set(CMAKE_OSX_SYSROOT "") # Prevent CMake from adding the -isysroot options
project(projectqcxx LANGUAGES CXX)

# Set a default build type if none was specified
if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  message(STATUS "Setting build type to 'Release' as none was specified.")
  set(CMAKE_BUILD_TYPE
      Release
      CACHE STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release"
                                               "RelWithDebInfo")
endif()

list(INSERT CMAKE_MODULE_PATH 0 ${CMAKE_CURRENT_LIST_DIR}/cmake)

#==============================================================================
# Setup compiler flags

include(${CMAKE_CURRENT_LIST_DIR}/cmake/compiler_flags.cmake)

#==============================================================================
# Options

include(${CMAKE_CURRENT_LIST_DIR}/cmake/options.cmake)

# ==============================================================================
# Package dependencies

include(${CMAKE_CURRENT_LIST_DIR}/cmake/packages.cmake)

# ==============================================================================
# Find pybind11

if(PYBIND11_DIR)
  message(STATUS "Using pybind11 from external directory: ${PYBIND11_DIR}")
  set(PYBIND11_INCLUDE_DIR "${PYBIND11_DIR}/include")
else()
  find_python_module(pybind11 REQUIRED)
  execute_process(
    COMMAND "${Python3_EXECUTABLE}" "-m" "pybind11" "--include"
    OUTPUT_STRIP_TRAILING_WHITESPACE
    OUTPUT_VARIABLE PYBIND11_INCLUDE_DIR)
endif()
include(${CMAKE_CURRENT_LIST_DIR}/cmake/pybind11.cmake)

# ==============================================================================

set(_projectq_sim_dir ${CMAKE_CURRENT_LIST_DIR}/projectq/backends/_sim)

add_python_module(_cppsim ${_projectq_sim_dir}/_cppsim.cpp)
target_include_directories(_cppsim PRIVATE ${_projectq_sim_dir}/_cppkernels/)

# ------------------------------------------------------------------------------
# Convenience target to automatically build all pybind11 C++ modules

add_custom_target(python DEPENDS ${_python_targets})

# ==============================================================================
