#   Copyright 2019 ProjectQ-Framework (www.projectq.ch)
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
"""
Registers decomposition for DiagonalGate
"""

from projectq.cengines import DecompositionRule
from projectq.meta import Compute, Control, Uncompute, CustomUncompute
from projectq.ops import (Ph, Rz, DiagonalGate, UniformlyControlledRz)

import numpy as np


def _calc_angle_phase(phi1, phi2):
    "Calculate angle and phase for diag -> diag + Rz decomposition"
    return .5 * (phi1 + phi2), (phi2 - phi1)


def _decompose_diag(cmd):
    """Recursively decompose a diagonal gate

      Decomposition of a diagonal gate follows theorem 7 from
      "Synthesis of Quantum Logic Circuits" by Shende et al.
      (https://arxiv.org/pdf/quant-ph/0406176.pdf).
    """
    diag = cmd.gate.diag
    qubits = cmd.qubits[0]
    assert len(cmd.control_qubits) == 0

    if 2**len(qubits) != len(diag):
        raise ValueError(
            "Wrong number of qubits compared to diagonal entries!")

    control_start_idx = 1
    target_idx = 0
    n = len(diag)
    while n > 1:
        angles = []
        for i in range(0, n, 2):
            # Reuse diag array to store the new diagonal coefficients
            # (ie. from index 0 to index n/2)
            diag[i // 2], angle = _calc_angle_phase(diag[i], diag[i + 1])
            angles.append(angle % (4 * np.pi))

        print(angles)
        controls = qubits[control_start_idx:]
        target = qubits[target_idx]
        UniformlyControlledRz(angles) | (controls, target)

        n >>= 1
        target_idx += 1
        control_start_idx += 1
    Ph(diag[0]) | target


#: Decomposition rules
all_defined_decomposition_rules = [
    DecompositionRule(DiagonalGate, _decompose_diag)
]
