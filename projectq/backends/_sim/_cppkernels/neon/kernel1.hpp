// Copyright 2020 ProjectQ-Framework (www.projectq.ch)
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

template <class V, class M>
inline void kernel_core(V& psi, std::size_t I, std::size_t d0, M const& m,
                        M const& mt)
{
     const float64x2x2_t v[2] = {load2(&psi[I]), load2(&psi[I + d0])};

     vst1q_f64_x2((double*) &psi[I + d0], (double*) &psi[I],
		  add(mul(v[0], m[0], mt[0]), mul(v[1], m[1], mt[1])));
}

// bit indices id[.] are given from high to low (e.g. control first for CNOT)
template <class V, class M>
void kernel(V& psi, unsigned id0, M const& m, std::size_t ctrlmask)
{
     const std::size_t n = psi.size();
     const std::size_t d0 = 1UL << id0;

     float64x2x2_t mm[] = {load(&m[0][0], &m[1][0]), load(&m[0][1], &m[1][1])};
     float64x2x2_t mmt[2];

     constexpr float64x2x2_t neg = {1.0, -1.0, 1.0, -1.0};
     for (unsigned i = 0; i < 2; ++i) {
          mmt[i] = vmulq_f64_x2(vpermq_f64_x2<5>(mm[i]), neg);
     }

     if (ctrlmask == 0) {
#pragma omp for collapse(LOOP_COLLAPSE1) schedule(static)
          for (std::size_t i0 = 0; i0 < n; i0 += 2 * d0) {
               for (std::size_t i1 = 0; i1 < d0; ++i1) {
                    kernel_core(psi, i0 + i1, d0, mm, mmt);
               }
          }
     }
     else {
#pragma omp for collapse(LOOP_COLLAPSE1) schedule(static)
          for (std::size_t i0 = 0; i0 < n; i0 += 2 * d0) {
               for (std::size_t i1 = 0; i1 < d0; ++i1) {
                    if (((i0 + i1) & ctrlmask) == ctrlmask)
                         kernel_core(psi, i0 + i1, d0, mm, mmt);
               }
          }
     }
}
