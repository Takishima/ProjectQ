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
inline void kernel_core(V& psi, std::size_t I, std::size_t d0, std::size_t d1,
                        M const& m, M const& mt)
{
     const float64x2x2_t v[4] = {load2(&psi[I]), load2(&psi[I + d0]),
                                 load2(&psi[I + d1]), load2(&psi[I + d0 + d1])};

     vst1q_f64_x2(
         (double*) &psi[I + d0], (double*) &psi[I],
         add(mul(v[0], m[0], mt[0]),
             add(mul(v[1], m[1], mt[1]),
                 add(mul(v[2], m[2], mt[2]), mul(v[3], m[3], mt[3])))));
     vst1q_f64_x2(
         (double*) &psi[I + d0 + d1], (double*) &psi[I + d1],
         add(mul(v[0], m[4], mt[4]),
             add(mul(v[1], m[5], mt[5]),
                 add(mul(v[2], m[6], mt[6]), mul(v[3], m[7], mt[7])))));
}

// bit indices id[.] are given from high to low (e.g. control first for CNOT)
template <class V, class M>
void kernel(V& psi, unsigned id1, unsigned id0, M const& m,
            std::size_t ctrlmask)
{
     const std::size_t n = psi.size();
     const std::size_t d0 = 1UL << id0;
     const std::size_t d1 = 1UL << id1;

     float64x2x2_t mm[] = {load(&m[0][0], &m[1][0]), load(&m[0][1], &m[1][1]),
                           load(&m[0][2], &m[1][2]), load(&m[0][3], &m[1][3]),
                           load(&m[2][0], &m[3][0]), load(&m[2][1], &m[3][1]),
                           load(&m[2][2], &m[3][2]), load(&m[2][3], &m[3][3])};
     float64x2x2_t mmt[8];

     constexpr float64x2x2_t neg = {1.0, -1.0, 1.0, -1.0};
     for (unsigned i = 0; i < 8; ++i) {
          mmt[i] = vmulq_f64_x2(vpermq_f64_x2<5>(mm[i]), neg);
     }

     const std::size_t dsorted[] = {d0 > d1 ? d0 : d1, d0 > d1 ? d1 : d0};

     if (ctrlmask == 0) {
#pragma omp for collapse(LOOP_COLLAPSE2) schedule(static)
          for (std::size_t i0 = 0; i0 < n; i0 += 2 * dsorted[0]) {
               for (std::size_t i1 = 0; i1 < dsorted[0]; i1 += 2 * dsorted[1]) {
                    for (std::size_t i2 = 0; i2 < dsorted[1]; ++i2) {
                         kernel_core(psi, i0 + i1 + i2, d0, d1, mm, mmt);
                    }
               }
          }
     }
     else {
#pragma omp for collapse(LOOP_COLLAPSE2) schedule(static)
          for (std::size_t i0 = 0; i0 < n; i0 += 2 * dsorted[0]) {
               for (std::size_t i1 = 0; i1 < dsorted[0]; i1 += 2 * dsorted[1]) {
                    for (std::size_t i2 = 0; i2 < dsorted[1]; ++i2) {
                         if (((i0 + i1 + i2) & ctrlmask) == ctrlmask)
                              kernel_core(psi, i0 + i1 + i2, d0, d1, mm, mmt);
                    }
               }
          }
     }
}
