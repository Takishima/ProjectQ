# -*- coding: utf-8 -*-
#
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

import math
import cmath
import numpy as np
from ._basics import BasicGate, ANGLE_PRECISION, ANGLE_TOLERANCE
from ._gates import R


def _round_to(angle, round_value): # pragma: no cover
    rounded_angle = round(float(angle) % (round_value), ANGLE_PRECISION)
    if rounded_angle > round_value - ANGLE_TOLERANCE:
        rounded_angle = 0.
    return rounded_angle


class U(BasicGate):
    """
    General unitary gate
    """
    def __init__(self, alpha, beta, gamma, delta):
        """
        Initialize a general unitary gate

        U(α, β, γ, λ) := exp(iα)Rz(β)Ry(γ)Rz(δ)

        Args:
            alpha (float): First angle of rotation (saved modulo 2 * pi)
            beta (float): Second angle of rotation (saved modulo 4 * pi)
            gamma (float): Third angle of rotation (saved modulo 4 * pi)
            delta (float): Third angle of rotation (saved modulo 4 * pi)
        """
        BasicGate.__init__(self)
        self.alpha = _round_to(alpha, 2 * math.pi)
        self.beta = _round_to(beta, 4 * math.pi)
        self.gamma = _round_to(gamma, 4 * math.pi)
        self.delta = _round_to(delta, 4 * math.pi)

    def __str__(self):
        """
        Return the string representation of an U3 gate

        Returns the class name and the angle as

        .. code-block:: python

            [CLASSNAME]([ANGLE])
        """
        return str(self.__class__.__name__) + "({}, {}, {}, {})".format(
            self.alpha, self.beta, self.gamma, self.delta)

    def tex_str(self):
        """
        Return the Latex string representation of an U3 gate

        Returns the class name and the angles as a subscript, i.e.

        .. code-block:: latex

            [CLASSNAME]$_[ANGLE]$
        """
        return str(self.__class__.__name__) + "$_{{{},{},{},{}}}$".format(
            self.alpha, self.beta, self.gamma, self.delta)

    def get_inverse(self):
        """
        Return the inverse of this unitary gate (negate the angles, return new
        object).
        """
        return U(-self.alpha, -self.delta, -self.gamma, -self.beta)

    def __eq__(self, other):
        """ Return True if same class and same rotation angle. """
        if isinstance(other, self.__class__):
            return ((self.alpha, self.beta, self.gamma,
                     self.delta) == (other.alpha, other.beta, other.gamma,
                                     other.delta))
        return False

    @property
    def matrix(self):
        bdp = self.beta + self.delta
        bdm = self.beta - self.delta
        cosg = cmath.cos(self.gamma / 2)
        sing = cmath.sin(self.gamma / 2)
        return cmath.exp(1j*self.alpha) * np.matrix(
            [[cmath.exp(-0.5j * bdp) * cosg, -cmath.exp(-0.5j * bdm) * sing],
             [cmath.exp(0.5j * bdm) * sing,
              cmath.exp(0.5j * bdp) * cosg]])


def U1(theta):
    """
    Diagonal single-qubit gate.

    Args:
        theta (float): Angle of rotation (saved modulo 4 * pi)
    """
    return R(theta)


class U2(U):
    """
    One pulse single-qubit gate (cf. IBM u2 gate)
    """
    def __init__(self, phi, lam):
        """
        Initialize an U2 gate

        Args:
            phi (float): First angle of rotation (saved modulo 4 * pi)
            lam (float): Second angle of rotation (saved modulo 4 * pi)
        """
        U.__init__(self, .5*(phi + lam), phi, np.pi/2, lam)

    def __str__(self):
        """
        Return the string representation of an U3 gate

        Returns the class name and the angle as

        .. code-block:: python

            [CLASSNAME]([ANGLE])
        """
        return str(self.__class__.__name__) + "({}, {})".format(
            self.beta, self.delta)

    def tex_str(self):
        """
        Return the LaTeX string representation of an U3 gate

        Returns the class name and the angles as a subscript, i.e.

        .. code-block:: latex

            [CLASSNAME]$_[ANGLE]$
        """
        return str(self.__class__.__name__) + "$_{{{},{}}}$".format(
            self.beta, self.delta)


class U3(U):
    """
    Two pulse single-qubit gate (cf. IBM u3 gate)
    """
    def __init__(self, theta, phi, lam):
        """
        Initialize an U3 gate

        Args:
            theta (float): First angle of rotation (saved modulo 2 * pi)
            phi (float): Second angle of rotation (saved modulo 4 * pi)
            lam (float): Third angle of rotation (saved modulo 4 * pi)
        """
        U.__init__(self, .5*(phi + lam), phi, theta, lam)

    def __str__(self):
        """
        Return the string representation of an U3 gate

        Returns the class name and the angle as

        .. code-block:: python

            [CLASSNAME]([ANGLE])
        """
        return str(self.__class__.__name__) + "({}, {}, {})".format(
            self.gamma, self.beta, self.delta)

    def tex_str(self):
        """
        Return the LaTeX string representation of an U3 gate

        Returns the class name and the angles as a subscript, i.e.

        .. code-block:: latex

            [CLASSNAME]$_[ANGLE]$
        """
        return str(self.__class__.__name__) + "$_{{{},{},{}}}$".format(
            self.gamma, self.beta, self.delta)


#: Symbols to automatically export
all_defined_symbols = [U1]
