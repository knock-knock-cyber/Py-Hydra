"""
    Module containing errors concerning hydra usage.
    Copyright (C) 2022  Knock Knock https://www.knock-knock.fr/

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License version 3 as published by
    the Free Software Foundation.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from errors.exceptions import CriticalException


class HydraError(CriticalException):
    """
    an unspecified hydra error
    """


class UnknownHydraError(HydraError):
    """
    Error used when the return code of hydra is not 0 and no specified errors was returned from hydra.
    """


class HydraDecodeError(HydraError):
    """
    Specific hydra error when the json is not decodable.
    """


class HydraUnsupportedServiceError(HydraError):
    """
    Error when an unsupported service is given to Hydra.
    """


class HydraUnknownServiceError(HydraError):
    """
    Error when an unknown service is given to Hydra.
    """


class HydraFileDoesNotExist(HydraError):
    """
    Error when the wordlist path given does not exist.
    """


class HydraNoWordlistGiven(HydraError):
    """
    No wordlist given, hydra can't start.
    """
