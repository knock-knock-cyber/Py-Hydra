"""
    This module implements the parsers used to retrieve info from the returns of THC-hydra.
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
import json
from typing import Dict

from errors.errors import HydraDecodeError


class HydraParser:
    """
    Hydra class that manages the method to parse the Hydra informations
    ...

    Methods
    -------
    json_opener():
        Open the Hydra output file.

    json2dict():
        Convert the json informations to a python dictionary.
    """

    @staticmethod
    def json_opener(json_path: str) -> Dict:
        """
        Method used to open the Hydra output.

        Parameters
        ----------
            json_path: str
                Hydra output path

        Returns
        -------
            hydra_json: Dict
                Dictionary with the json informations

        Raises:
        -------
            json.decoder.JSONDecodeError: If the method can't load the file from the given path.
        """
        try:
            with open(json_path, "r", encoding="utf-8") as credentials:
                hydra_json: Dict = json.load(credentials)
            return hydra_json
        except json.decoder.JSONDecodeError as e:
            raise HydraDecodeError(
                f"Can't open the given file : {json_path}. Please make sure it is a JSON file."
            ) from e

    @staticmethod
    def json2dict(json_path: str) -> Dict:
        """
        Method used to convert a json file to a python dictionary containing the working credentials.

        Args:
            json_path: str
                Hydra output path

        Returns:
            working_creds: Dict
                Dictionary with the working credentials.

        Raises:
        -------
            KeyError: If the method can't find the logins from the JSON file.
        """
        hydra_output = HydraParser.json_opener(json_path)
        try:
            login = [login["login"] for login in hydra_output["results"]]
            password = [password["password"] for password in hydra_output["results"]]
            working_creds = dict(zip(login, password))
            return working_creds
        except KeyError as e:
            raise HydraDecodeError(f"Couldn't parse any Hydra information from the json file: {json_path}") from e


if __name__ == "__main__":
    HydraParser().json2dict("logs_full_.json")
