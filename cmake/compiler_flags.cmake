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

# C++ standard falgs
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_EXTENSIONS OFF)

# Always generate position independent code
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

# ------------------------------------------------------------------------------

check_compiler_flags(_compile_flags_release "-ffast-math /fp:fast -fast"
                     "-O3 /Ox")

check_compiler_flags(_archnative_flag "-march=native -xHost /QxHost /arch:AVX2")

if(NOT _archnative_flag_cxx)
  message(FATAL_ERROR "Unable to find compiler flag for compiler intrinsics")
endif()

# --------------------------------------

add_compile_options(
  "$<$<AND:$<CONFIG:RELEASE>,$<COMPILE_LANGUAGE:CXX>>:${_compile_flags_release_cxx}>"
  "$<$<COMPILE_LANGUAGE:CXX>:${_archnative_flag_cxx}>")

# ==============================================================================
# Platform specific flags

if(WIN32)
  add_definitions(-D_USE_MATH_DEFINES -D_CRT_SECURE_NO_WARNINGS)
  add_definitions(-DWIN32_LEAN_AND_MEAN)
endif()
