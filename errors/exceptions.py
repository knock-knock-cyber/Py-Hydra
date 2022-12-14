"""
    Module defining base exceptions.
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
import logging


class CriticalException(Exception):
    """
    Class implementing the base CriticalException of the ToolBox.
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        self.log(*args)

    @staticmethod
    def log(*args):
        """
        Method used for logging the critical exception.
        """
        logging.critical(*args)


class UnsupportedOSError(CriticalException):
    """Error used when we try to process an unsupported OS host."""


class ExceptionMessages:
    """
    Class used to store the messages of the most common errors.
    """

    @staticmethod
    def invalid_type(param_name: str, object_: object, expected_type) -> str:
        """
        This method construct the error message for invalid types given to methods.

        Parameters
        ----------
        param_name: str
            The name of the parameter with invalid type.

        object_: object
            The parameter given which does not have the right type

        expected_type:
            The expected type.

        Returns
        -------
        str
        """
        return f"{param_name} is {type(object_)}, expected {expected_type}"

    @staticmethod
    def invalid_list_types(param_name: str, expected_type) -> str:
        """
        This method construct the error message for list containing invalid types.

        Parameters
        ----------
        param_name: str
            The name of the parameter containing a list of invalid types.

        expected_type:
            The expected type inside the list.

        Returns
        -------
        str
        """
        return f"{param_name} must be a list of {expected_type}"


class WarningMessages:
    """
    Class used to store the messages of the most common warnings.
    """

    @staticmethod
    def invalid_equal_types(self_object, other_object) -> str:
        """
        This method construct the warning message when a comparison between invalid types is done.

        Parameters
        ----------
        self_object
            First object of the comparison.

        other_object
            Second object of the comparison.

        Returns
        -------
        str
        """
        return f"You tried to make an equality comparison between a {type(self_object)} and a {type(other_object)}."
