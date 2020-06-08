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

#ifndef CINTRIN_HPP_
#define CINTRIN_HPP_

#include <arm_neon.h>

#include <complex>
#include <utility>

#define FORCE_INLINE __attribute__((always_inline)) inline

template <uint8_t imm8>
float64x2x2_t vpermq_f64_x2(float64x2x2_t a)
{
     float64x2x2_t res;
     if (imm8 & 1 && (imm8 >> 1) & 1) {
          res.val[0] = vcombine_f64(vget_high_f64(a.val[0]), vget_high_f64(a.val[0]));
     }
     else if ((imm8 >> 1) & 1) {
          res.val[0] = vcombine_f64(vget_low_f64(a.val[0]), vget_high_f64(a.val[0]));
     }
     else if (imm8 & 1) {
          res.val[0] = vcombine_f64(vget_high_f64(a.val[0]), vget_low_f64(a.val[0]));
     }
     else {
          res.val[0] = vcombine_f64(vget_low_f64(a.val[0]), vget_low_f64(a.val[0]));
     }

     if ((imm8 >> 2) & 1 && (imm8 >> 3) & 1) {
          res.val[1] = vcombine_f64(vget_high_f64(a.val[1]), vget_high_f64(a.val[1]));
     }
     else if ((imm8 >> 3) & 1) {
          res.val[1] = vcombine_f64(vget_low_f64(a.val[1]), vget_high_f64(a.val[1]));
     }
     else if ((imm8 >> 2) & 1) {
          res.val[1] = vcombine_f64(vget_high_f64(a.val[1]), vget_low_f64(a.val[1]));
     }
     else {
          res.val[1] = vcombine_f64(vget_low_f64(a.val[1]), vget_low_f64(a.val[1]));
     }

     return res;
}

float64x2x2_t vdupq_n_f64_x2(double a)
{
     auto tmp = vmov_n_f64(a);
     return {vcombine_f64(tmp, tmp), vcombine_f64(tmp, tmp)};
}

void vst1q_f64_x2(float64_t* hi, float64_t* lo, float64x2x2_t a)
{
     vst1q_f64(hi, a.val[0]);
     vst1q_f64(lo, a.val[1]);
}

float64x2x2_t vhsubq_f64_x2(float64x2x2_t a, float64x2x2_t b)
{
     return {vcombine_f64(
                 vsub_f64(vget_low_f64(a.val[0]), vget_high_f64(a.val[0])),
                 vsub_f64(vget_low_f64(b.val[0]), vget_high_f64(b.val[0]))),
             vcombine_f64(
                 vsub_f64(vget_low_f64(a.val[1]), vget_high_f64(a.val[1])),
                 vsub_f64(vget_low_f64(b.val[1]), vget_high_f64(b.val[1])))};

     // Lead to the same assembly code (tested with Clang and optimizations on)
     // float64x1_t* tmpa = reinterpret_cast<float64_t*>(&a.val[0]);
     // float64x1_t* tmpb = reinterpret_cast<float64_t*>(&b.val[0]);
     // return {vcombine_f64(
     // 	       vsub_f64(tmpa[0], tmpa[1]),
     // 	       vsub_f64(tmpb[0], tmpb[1])),
     // 	     vcombine_f64(
     // 	       vsub_f64(tmpa[2], tmpa[3]),
     // 	       vsub_f64(tmpb[2], tmpb[3]))
     // };
}

float64x2x2_t vmulq_f64_x2(float64x2x2_t a, float64x2x2_t b)
{
     return {vmulq_f64(a.val[0], b.val[0]), vmulq_f64(a.val[1], b.val[1])};
}


template <class T>
class cintrin;

template <>
class cintrin<double>
{
public:
     using calc_t = double;
     using ret_t = cintrin<calc_t>;

     cintrin()
     {}

     template <class U>
     cintrin(U const* p) : v_(vld1q_f64_x2((const calc_t*) p))
     {}

     template <class U>
     cintrin(U const* p1, U const* p2)
         : v_({vld1q_f64((const calc_t*) p2), vld1q_f64((const calc_t*) p1)})
     {}

     template <class U>
     cintrin(U const* p, bool)
         : v_({vld1q_f64((calc_t const*) p), vld1q_f64((calc_t const*) p)})
     {}

     explicit cintrin(calc_t const& s1) : v_(vdupq_n_f64_x2(s1))
     {}

     cintrin(float64x2x2_t const& v) : v_(v)
     {}

     std::complex<calc_t> operator[](unsigned i)
     {
          calc_t v[4];
          vst1q_f64_x2(v, v_);
          return {v[i * 2], v[i * 2 + 1]};
     }

     template <class U>
     void store(U* p) const
     {
          vst1q_f64_x2((calc_t*) p, v_);
     }

     template <class U>
     void store(U* p1, U* p2) const
     {
          vst1q_f64((calc_t*) p2, v_.val[0]);
          vst1q_f64((calc_t*) p1, v_.val[1]);
     }
     float64x2x2_t v_;
};

inline cintrin<double> mul(cintrin<double> const& c1, cintrin<double> const& c2,
                           cintrin<double> const& c2tm)
{
     const auto ac_bd = vmulq_f64_x2(c1.v_, c2.v_);
     const auto multbmadmc = vmulq_f64_x2(c1.v_, c2tm.v_);
     return cintrin<double>(vhsubq_f64_x2(ac_bd, multbmadmc));
}
inline cintrin<double> operator*(cintrin<double> const& c1,
                                 cintrin<double> const& c2)
{
     float64x2x2_t neg = {1., -1., 1., -1.};
     const auto badc = vpermq_f64_x2<5>(c2.v_);
     const auto bmadmc = vmulq_f64_x2(badc, neg);
     return mul(c1, c2, bmadmc);
}
inline cintrin<double> operator+(cintrin<double> const& c1,
                                 cintrin<double> const& c2)
{
     float64x2x2_t tmp = {vaddq_f64(c1.v_.val[0], c2.v_.val[0]),
                          vaddq_f64(c1.v_.val[1], c2.v_.val[1])};
     return cintrin<double>(tmp);
}
inline cintrin<double> operator*(cintrin<double> const& c1, double const& d)
{
     const auto d_d = vdupq_n_f64_x2(d);
     return vmulq_f64_x2(c1.v_, d_d);
}
inline cintrin<double> operator*(double const& d, cintrin<double> const& c1)
{
     return c1 * d;
}

inline float64x2x2_t mul(float64x2x2_t const& c1, float64x2x2_t const& c2,
                         float64x2x2_t const& c2tm)
{
     auto ac_bd = vmulq_f64_x2(c1, c2);
     auto multbmadmc = vmulq_f64_x2(c1, c2tm);
     return vhsubq_f64_x2(ac_bd, multbmadmc);
}
inline float64x2x2_t add(float64x2x2_t const& c1, float64x2x2_t const& c2)
{
     return
     {
          vaddq_f64(c1.val[0], c2.val[0]), vaddq_f64(c1.val[1], c2.val[1])
     };
}
template <class U>
inline float64x2x2_t load2(U* p)
{
     const auto tmp = vld1q_f64((double const*) p);
     return {tmp, tmp};
}
template <class U>
inline float64x2x2_t load(U const* p1, U const* p2)
{
     return {vld1q_f64((double const*) p2), vld1q_f64((double const*) p1)};
}
#endif
