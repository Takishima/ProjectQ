#   Copyright 2018 ProjectQ-Framework (www.projectq.ch)
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

import math
import cmath

from ._basics import (ATOL, ANGLE_PRECISION, ANGLE_TOLERANCE, BasicGate,
                      NotMergeable)


class UniformlyControlledRot(BasicGate):
    def __init__(self, axis, angles):
        BasicGate.__init__(self)

        assert axis in 'YZ'
        self.axis = axis

        rounded_angles = []
        for angle in angles:
            new_angle = round(float(angle) % (4. * math.pi), ANGLE_PRECISION)
            if new_angle > 4 * math.pi - ANGLE_TOLERANCE:
                new_angle = 0.
            rounded_angles.append(new_angle)
        self.angles = rounded_angles

    def get_inverse(self):
        return self.__class__([-1 * angle for angle in self.angles])

    def get_merged(self, other):
        if isinstance(other, self.__class__):
            new_angles = [
                angle1 + angle2
                for (angle1, angle2) in zip(self.angles, other.angles)
            ]
            return self.__class__(new_angles)
        raise NotMergeable()

    def __str__(self):
        return "UniformlyControlledRot(" + self.axis + ", " + str(
            self.angles) + ")"

    def __eq__(self, other):
        """ Return True if same class, same rotation angles."""
        if isinstance(other, self.__class__):
            return self.angles == other.angles
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))


class UniformlyControlledRy(UniformlyControlledRot):
    """
    Uniformly controlled Ry gate as introduced in arXiv:quant-ph/0312218.

    This is an n-qubit gate. There are n-1 control qubits and one target qubit.
    This gate applies Ry(angles(k)) to the target qubit if the n-1 control
    qubits are in the classical state k. As there are 2^(n-1) classical
    states for the control qubits, this gate requires 2^(n-1) (potentially
    different) angle parameters.

    Example:
        .. code-block:: python

        controls = eng.allocate_qureg(2)
        target = eng.allocate_qubit()
        UniformlyControlledRy(angles=[0.1, 0.2, 0.3, 0.4]) | (controls, target)

    Note:
        The first quantum register contains the control qubits. When converting
        the classical state k of the control qubits to an integer, we define
        controls[0] to be the least significant (qu)bit. controls can also
        be an empty list in which case the gate corresponds to an Ry.

    Args:
        angles(list[float]): Rotation angles. Ry(angles[k]) is applied
                             conditioned on the control qubits being in state
                             k.
    """
    def __init__(self, angles):
        UniformlyControlledRot.__init__(self, 'Y', angles)


class UniformlyControlledRz(UniformlyControlledRot):
    """
    Uniformly controlled Rz gate as introduced in arXiv:quant-ph/0312218.

    This is an n-qubit gate. There are n-1 control qubits and one target qubit.
    This gate applies Rz(angles(k)) to the target qubit if the n-1 control
    qubits are in the classical state k. As there are 2^(n-1) classical
    states for the control qubits, this gate requires 2^(n-1) (potentially
    different) angle parameters.

    Example:
        .. code-block:: python

        controls = eng.allocate_qureg(2)
        target = eng.allocate_qubit()
        UniformlyControlledRz(angles=[0.1, 0.2, 0.3, 0.4]) | (controls, target)

    Note:
        The first quantum register are the contains qubits. When converting
        the classical state k of the control qubits to an integer, we define
        controls[0] to be the least significant (qu)bit. controls can also
        be an empty list in which case the gate corresponds to an Rz.

    Args:
        angles(list[float]): Rotation angles. Rz(angles[k]) is applied
                             conditioned on the control qubits being in state
                             k.
    """
    def __init__(self, angles):
        UniformlyControlledRot.__init__(self, 'Z', angles)


class DiagonalGate(BasicGate):
    """
    Implement a diagonal gate defined by 2^k diagonal entries
    (k number of qubits)

    .. note::

      Decomposition of the diagonal gate follows theorem 7 from
      "Synthesis of Quantum Logic Circuits" by Shende et al.
      (https://arxiv.org/pdf/quant-ph/0406176.pdf).
    """
    def __init__(self, diag):
        BasicGate.__init__(self)
        num_qubits = len(diag)
        if not (num_qubits > 1 and not (num_qubits & (num_qubits - 1))):
            raise RuntimeError(
                "Number of diagonal entries must be a power of 2!")

        self.diag = []
        for d in diag:
            if abs(d) - 1 > ATOL:
                raise ValueError(
                    "The absolute value of all diagonal entries must be 1!")
            self.diag.append(cmath.phase(d))

    def get_inverse(self):
        return self.__class__([cmath.exp(-1j * d) for d in self.diag])

    def get_merged(self, other):
        if isinstance(other, self.__class__):
            return self.__class__([
                cmath.exp(1j * (d1 + d2))
                for (d1, d2) in zip(self.diag, other.diag)
            ])
        raise NotMergeable()

    def __str__(self):
        return "DiagonalGate(" + str([cmath.exp(1j * d)
                                      for d in self.diag]) + ")"

    def __eq__(self, other):
        """ Return True if same class, same diagonal entries."""
        if isinstance(other, self.__class__):
            return self.diag == other.diag
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self))
