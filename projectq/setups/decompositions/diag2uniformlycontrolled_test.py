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
"""Tests for projectq.setups.decompositions.diag2uniformlycontrolled."""

import pytest

import numpy as np

from projectq import MainEngine
from projectq.backends import Simulator
from projectq.cengines import (AutoReplacer, DecompositionRuleSet, DummyEngine,
                               InstructionFilter)

from projectq.ops import (All, Measure, MatrixGate, UniformlyControlledRz,
                          DiagonalGate)

import projectq.setups.decompositions.uniformlycontrolledr2cnot as ucr2cnot
import projectq.setups.decompositions.diag2uniformlycontrolled as diag2ucr

# ==============================================================================


def _decomp_gates(eng, cmd):
    if isinstance(cmd.gate, (UniformlyControlledRz, DiagonalGate)):
        return False
    return True


@pytest.fixture
def autoreplacer():
    rule_set = DecompositionRuleSet(modules=[ucr2cnot, diag2ucr])
    return AutoReplacer(rule_set)


@pytest.fixture
def default_engine_list(autoreplacer):
    return [autoreplacer, InstructionFilter(_decomp_gates)]


# ==============================================================================


def test_identity(default_engine_list):
    eng = MainEngine(engine_list=default_engine_list)
    qureg = eng.allocate_qureg(6)
    ref = eng.backend.cheat()
    DiagonalGate([1] * 2**len(qureg)) | qureg
    eng.flush()
    assert ref == eng.backend.cheat()


def test_wrong_number_of_diag_entries(default_engine_list):
    eng = MainEngine(backend=DummyEngine(), engine_list=default_engine_list)
    qureg = eng.allocate_qureg(4)
    with pytest.raises(ValueError):
        DiagonalGate([1] * 4) | qureg


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_uniformly_controlled_ry(n, default_engine_list):
    random_angles = [
        0.5, 0.8, 1.2, 2.5, 4.4, 2.32, 6.6, 15.12, 1, 2, 9.54, 2.1, 3.1415,
        1.1, 0.01, 0.99
    ]

    diag = [np.exp(1j * a) for a in random_angles[:2**n]]

    for basis_state_index in range(0, 2**n):
        basis_state = [0] * 2**n
        basis_state[basis_state_index] = 1.
        correct_dummy_eng = DummyEngine(save_commands=True)
        correct_eng = MainEngine(backend=Simulator(),
                                 engine_list=[correct_dummy_eng])
        test_dummy_eng = DummyEngine(save_commands=True)
        test_eng = MainEngine(backend=Simulator(),
                              engine_list=default_engine_list +
                              [test_dummy_eng])
        test_sim = test_eng.backend
        correct_sim = correct_eng.backend
        correct_qureg = correct_eng.allocate_qureg(n)
        correct_eng.flush()
        test_qureg = test_eng.allocate_qureg(n)
        test_eng.flush()

        correct_sim.set_wavefunction(basis_state, correct_qureg)
        test_sim.set_wavefunction(basis_state, test_qureg)

        DiagonalGate(diag) | (test_qureg)
        MatrixGate(np.diagflat(diag)) | correct_qureg

        test_eng.flush()
        correct_eng.flush()

        for fstate in range(2**n):
            binary_state = format(fstate, '0' + str(n + 1) + 'b')
            test = test_sim.get_amplitude(binary_state, test_qureg)
            correct = correct_sim.get_amplitude(binary_state, correct_qureg)
            assert correct == pytest.approx(test, rel=1e-10, abs=1e-10)

        assert correct_sim.cheat()[1] == pytest.approx(test_sim.cheat()[1],
                                                       rel=1e-10,
                                                       abs=1e-10)
        All(Measure) | test_qureg
        All(Measure) | correct_qureg
        test_eng.flush(deallocate_qubits=True)
        correct_eng.flush(deallocate_qubits=True)
