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

include(CMakeDependentOption)

# ------------------------------------------------------------------------------

if(APPLE)
  option(
    PYTHON_VIRTUALENV_COMPAT
    "(Mac OS X) Make CMake search for Python Framework *after* any available\
  unix-style package. Can be useful in case of virtual environments." ON)
else()
  option(
    PYTHON_VIRTUALENV_COMPAT
    "(Mac OS X) Make CMake search for Python Framework *after* any available\
  unix-style package. Can be useful in case of virtual environments." OFF)
endif()

# ------------------------------------------------------------------------------

option(BUILD_TESTING "Build the test suite?" OFF)

# ------------------------------------------------------------------------------

option(IS_PYTHON_BUILD
       "Is CMake called from Python? (e.g. python3 setup.py install?)" OFF)

# ==============================================================================

if(PYTHON_VIRTUALENV_COMPAT)
  set(CMAKE_FIND_FRAMEWORK LAST)
endif()

# ------------------------------------------------------------------------------
