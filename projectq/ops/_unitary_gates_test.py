#   Copyright 2020 ProjectQ-Framework (www.projectq.ch)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""Tests for projectq.ops._unitary_gates."""

import pytest
import cmath
import math
import numpy as np

from projectq.ops import R, U, U1, U2, U3, get_inverse


@pytest.mark.parametrize("alpha", [0, 2.2, 2 * math.pi])
@pytest.mark.parametrize("beta",  [0, 2.3, 2 * math.pi, 4 * math.pi])
@pytest.mark.parametrize("gamma", [0, 2.4, 2 * math.pi, 4 * math.pi])
@pytest.mark.parametrize("delta", [0, 2.5, 2 * math.pi, 4 * math.pi])
def test_u_gate(alpha, beta, gamma, delta):
    gate = U(alpha, beta, gamma, delta)
    bdp = beta + delta
    bdm = beta - delta
    cosg = cmath.cos(gamma / 2)
    sing = cmath.sin(gamma / 2)
    # yapf: disable
    expected_matrix = cmath.exp(1j*alpha) * np.matrix(
        [
            [cmath.exp(-0.5j * bdp) * cosg,
             -cmath.exp(-0.5j * bdm) * sing],
            [cmath.exp(0.5j * bdm) * sing,
             cmath.exp(0.5j * bdp) * cosg]
        ])
    # yapf: enable
    assert gate.matrix.shape == expected_matrix.shape
    assert np.allclose(gate.matrix, expected_matrix)
    assert np.allclose(np.dot(gate.matrix,
                              get_inverse(gate).matrix), np.eye(2))


@pytest.mark.parametrize("theta", [0, 2.1, 2 * math.pi, 4 * math.pi])
@pytest.mark.parametrize("phi",   [0, 2.2, 2 * math.pi, 4 * math.pi])
@pytest.mark.parametrize("lam",   [0, 2.3, 2 * math.pi, 4 * math.pi])
def test_u3_gate(theta, phi, lam):
    gate = U3(theta, phi, lam)
    # yapf: disable
    expected_matrix = np.matrix([
            [
                np.cos(theta / 2),
                -np.exp(1j * lam) * np.sin(theta / 2)
            ],
            [
                np.exp(1j * phi) * np.sin(theta / 2),
                np.exp(1j * (phi + lam)) * np.cos(theta / 2)
            ]
        ])
    # yapf: enable
    assert gate.matrix.shape == expected_matrix.shape
    assert np.allclose(gate.matrix, expected_matrix)
    assert np.allclose(np.dot(gate.matrix,
                              get_inverse(gate).matrix), np.eye(2))


@pytest.mark.parametrize("phi", [0, 3.1, 2 * math.pi, 4 * math.pi])
@pytest.mark.parametrize("lam", [0, 3.2, 2 * math.pi, 4 * math.pi])
def test_u2_gate(phi, lam):
    gate = U2(phi, lam)
    # yapf: disable
    theta = np.pi/2
    expected_matrix = np.matrix([
            [
                np.cos(theta / 2),
                -np.exp(1j * lam) * np.sin(theta / 2)
            ],
            [
                np.exp(1j * phi) * np.sin(theta / 2),
                np.exp(1j * (phi + lam)) * np.cos(theta / 2)
            ]
        ])
    # yapf: enable
    assert gate.matrix.shape == expected_matrix.shape
    assert np.allclose(gate.matrix, expected_matrix)
    assert np.allclose(np.dot(gate.matrix,
                              get_inverse(gate).matrix), np.eye(2))


@pytest.mark.parametrize("lam", [0, 0.2, 2.1, 4.1, 2 * math.pi, 4 * math.pi])
def test_u1(lam):
    gate = U1(lam)
    assert np.allclose(gate.matrix, R(lam).matrix)
    assert np.allclose(np.dot(gate.matrix,
                              get_inverse(gate).matrix), np.eye(2))


def test_u_u2_u3_str():
    gate = U(1, 2, 3, 4)
    gate_str = str(gate)
    gate_tex = gate.tex_str()

    assert gate_str == 'U(1.0, 2.0, 3.0, 4.0)'
    assert gate_tex == 'U$_{1.0,2.0,3.0,4.0}$'

    gate = U3(2, 3, 4)
    gate_str = str(gate)
    gate_tex = gate.tex_str()

    assert gate_str == 'U3(2.0, 3.0, 4.0)'
    assert gate_tex == 'U3$_{2.0,3.0,4.0}$'

    gate = U2(3, 4)
    gate_str = str(gate)
    gate_tex = gate.tex_str()

    assert gate_str == 'U2(3.0, 4.0)'
    assert gate_tex == 'U2$_{3.0,4.0}$'


def test_u_equality():
    gate = U(1, 2, 3, 4)
    assert gate == U(1, 2, 3, 4)
    assert not (gate == U(0, 2, 3, 4))
    assert gate != U(0, 2, 3, 4)
    assert gate != U3(1, 2, 3)
