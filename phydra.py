"""
    Phydra, a python interface for thc-hydra.
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
import os
import subprocess
import tempfile
import logging

from ipaddress import ip_address
from typing import Dict, Optional, List, Union
from errors.exceptions import ExceptionMessages
from errors.errors import (
    HydraError,
    HydraFileDoesNotExist,
    HydraNoWordlistGiven,
    HydraUnsupportedServiceError,
    HydraUnknownServiceError,
    UnknownHydraError,
)
from modules.hydraparser import HydraParser


class Hydra:
    """
    Hydra class that manages the Hydra methods and output.
    ...

    Methods
    -------
    bruteforce():
        Start the bruteforce.
    """

    def __init__(self, ip: str, hydra_path: str = "/usr/bin/hydra"):
        """
        Parameters
        ----------
           ip: str
                An IPv6 or IPv4 IP.
        """
        self.ip = ip_address(ip)
        if not os.path.exists(hydra_path):
            raise AttributeError(
                f"Hydra not found on path '{hydra_path}', "
                f"please install it using : sudo apt install hydra\n"
                f"If hydra is installed, provide the absolute path using hydra_path="
            )
        self.hydra_path = hydra_path
        self.hydra_args: Dict[str, str] = {
            "UserWordlist": "-L",
            "Username": "-l",
            "PassWordlist": "-P",
            "Password": "-p",
            "Threads": "-t",
            "OutputFilename": "-o",
            "OutputType": "-b",
            "IgnoreRestoreFile": "-I",
            "Port": "-s",
            "UserPassWordlist": "-C",
        }
        self.valid_outputs: List = ["text", "json", "jsonv1"]

        self.hydra_settings: Dict = {}
        for hydra_setting in self.hydra_args.values():
            self.hydra_settings.update({hydra_setting: ""})

        self.service: Optional[str] = None
        self.port: Optional[int] = None
        self.user_wordlist: Optional[str] = None
        self.pass_wordlist: Optional[str] = None
        self.threads: int = 4
        self.export_type: str = "json"
        self.delete_export: bool = True
        self.ignore_restore_file: bool = True

        self.service_without_user = ["redis", "adam6500", "cisco", "oracle-listener", "s7-300", "snmp", "vnc"]
        with open(os.path.join(os.path.dirname(__file__), "services/supported_services"), "r", encoding="utf-8") as f:
            self.supported_services = f.read().splitlines()
        with open(os.path.join(os.path.dirname(__file__), "services/special_services"), "r", encoding="utf-8") as f:
            self.unsupported_services = f.read().splitlines()

    def bruteforce(
        self,
        service: str,
        port: Union[int, str],
        user_wordlist: Optional[str] = None,
        pass_wordlist: Optional[str] = None,
        threads: Union[str, int] = 4,
        export_type: str = "json",
        ignore_restore_file: bool = True,
        wait_time: int = 2,
    ) -> Dict:
        """
        Method to start the Hydra bruteforce.

        Parameters
        ----------
            service: str
                Service name.
            port: Union[int, str]
                Port number
                Is the -s parameter from Hydra.
            user_wordlist: str
                Path to usernames wordlist
                Is the -L parameter from Hydra.
            pass_wordlist: str
                Path to passwords wordlist
                Is the -P parameter from Hydra.
            threads: int, optional
                Number of threads, up to 64. Defaults to 4.
                Is the -t parameter from Hydra.
            export_type: str, optional
                Export type for data analysis. Defaults to json.
                Is the -b parameter from Hydra.
            ignore_restore_file: bool, optional
                Ignore the Hydra restore file. Defaults to True.
                Is the -I parameter from Hydra.
            wait_time: int, optional
                Change the time out of hydra. By default: 2

        Returns
        -------
            Dict
                Dictionary containing the working credentials.
                {'username': username, 'password': password}
        """
        # Check inputs
        if user_wordlist is None:
            logging.warning("No user wordlist given")
        else:
            if not isinstance(user_wordlist, str):
                raise TypeError(ExceptionMessages.invalid_type("user_wordlist", user_wordlist, str))

        if pass_wordlist is None:
            logging.warning("No pass wordlist given")
        else:
            if not isinstance(pass_wordlist, str):
                raise TypeError(ExceptionMessages.invalid_type("pass_wordlist", pass_wordlist, str))

        if not isinstance(service, str):
            raise TypeError(ExceptionMessages.invalid_type("service", service, str))

        if not isinstance(port, str) and not isinstance(port, int):
            raise TypeError(ExceptionMessages.invalid_type("port", port, "str or int"))

        try:
            port = int(port)
        except ValueError as e:
            raise ValueError(f"The port number should be an integer, {port} was given.") from e

        if not isinstance(threads, int):
            raise TypeError(ExceptionMessages.invalid_type("threads", threads, int))
        if not isinstance(export_type, str):
            raise TypeError(ExceptionMessages.invalid_type("export_type", export_type, str))

        if not isinstance(ignore_restore_file, bool):
            raise TypeError(ExceptionMessages.invalid_type("ignore_restore_file", ignore_restore_file, bool))

        if not isinstance(wait_time, int):
            raise TypeError(ExceptionMessages.invalid_type("wait_time", wait_time, int))

        if export_type not in self.valid_outputs:
            raise ValueError(f"{export_type} is not a valid export type, use 'text', 'json' or 'jsonv1'")

        if threads >= 65:
            logging.info(f"Threads given is too high, {threads}, reducing to 64.")
            self.threads = 64
        else:
            self.threads = threads

        service = service.lower()
        export_type = export_type.lower()

        # Check if the given service is supported
        if service not in self.supported_services:
            if service in self.unsupported_services:
                raise HydraUnsupportedServiceError(f"Unsupported service given : {service}")
            raise HydraUnknownServiceError(f"Unknown service: {service}")

        with tempfile.NamedTemporaryFile() as tmp_file:
            command_string = self._user_and_pass_wordlists_string_generator(
                threads,
                wait_time,
                service,
                port,
                export_type,
                ignore_restore_file,
                user_wordlist,
                pass_wordlist,
                tmp_file.name,
            )
            self._running_command(command_string)
            json_dict = HydraParser.json2dict(tmp_file.name)

        return json_dict

    def bruteforce_with_userpass_wordlist(
        self,
        service: str,
        port: Union[int, str],
        userpass_wordlist_path: str,
        threads: Union[str, int] = 4,
        export_type: str = "json",
        ignore_restore_file: bool = True,
        wait_time: int = 2,
    ):
        """
        Bruteforce with a userpass wordlist.
        userpass wordlist example:
        root:root
        ubuntu:ubuntu

        Parameters
        ----------
        service : str
            Name of the service
        port : Union[int, str]
            Port the service is running on
        userpass_wordlist_path : str
            Path of the wordlist
        threads : Union[str, int], optional
            Threads used to bruteforce, by default 4
        export_type: str, optional
                Export type for data analysis. Defaults to json.
                Is the -b parameter from Hydra.
        ignore_restore_file: bool, optional
            Ignore the Hydra restore file. Defaults to True.
            Is the -I parameter from Hydra.
        wait_time: int, optional
            Change the time out of hydra. By default: 2

        Returns
        -------
        Dict
            Dictionary containing the working credentials.
            {'username': username, 'password': password}

        Raises
        ------
        TypeError
            An argument does not have the correct type
        HydraUnsupportedServiceError
            The selected service is not supported by Hydra
        HydraUnknownServiceError
            Service unknown
        """
        if not isinstance(userpass_wordlist_path, str):
            raise TypeError(ExceptionMessages.invalid_type("userpass_wordlist_path", userpass_wordlist_path, str))
        if not os.path.isfile(os.path.abspath(userpass_wordlist_path)):
            raise TypeError("Wordlist path does not exist")

        userpass_wordlist_path = os.path.abspath(userpass_wordlist_path)

        if not isinstance(service, str):
            raise TypeError(ExceptionMessages.invalid_type("service", service, str))

        if not isinstance(port, str) and not isinstance(port, int):
            raise TypeError(ExceptionMessages.invalid_type("port", port, "str or int"))

        try:
            port = int(port)
        except ValueError as e:
            raise ValueError(f"The port number should be an integer, {port} was given.") from e

        if not isinstance(threads, int):
            raise TypeError(ExceptionMessages.invalid_type("threads", threads, int))
        if not isinstance(export_type, str):
            raise TypeError(ExceptionMessages.invalid_type("export_type", export_type, str))

        if not isinstance(ignore_restore_file, bool):
            raise TypeError(ExceptionMessages.invalid_type("ignore_restore_file", ignore_restore_file, bool))

        if not isinstance(wait_time, int):
            raise TypeError(ExceptionMessages.invalid_type("wait_time", wait_time, int))

        if export_type not in self.valid_outputs:
            raise ValueError(f"{export_type} is not a valid export type, use 'text', 'json' or 'jsonv1'")

        if threads >= 65:
            logging.warning(f"Threads given is too high, {threads}, reducing to 64.")
            self.threads = 64
        else:
            self.threads = threads

        service = service.lower()
        export_type = export_type.lower()

        # Check if the given service is supported
        if service not in self.supported_services:
            if service in self.unsupported_services:
                raise HydraUnsupportedServiceError(f"Unsupported service given : {service}")
            raise HydraUnknownServiceError(f"Unknown service: {service}")

        with tempfile.NamedTemporaryFile() as tmp_file:
            command_string = self._userpass_wordlist_string_generator(
                threads,
                wait_time,
                service,
                port,
                export_type,
                ignore_restore_file,
                userpass_wordlist_path,
                tmp_file.name,
            )
            self._running_command(command_string)
            json_dict = HydraParser.json2dict(tmp_file.name)

        return json_dict

    @staticmethod
    def _running_command(command_string: str):
        """Run a given Hydra command"""
        logging.info(f"Running thc-hydra with following command : {command_string}")

        with subprocess.Popen(
            command_string.split(), stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
        ) as hydra_command:

            exit_code = hydra_command.wait()
            _, stderr = hydra_command.communicate()
            hydra_messages = stderr.decode().split("\n")

            for hydra_message in hydra_messages:
                if hydra_message.startswith("[WARNING]"):
                    logging.warning(hydra_message)
            if exit_code != 0:

                for hydra_error in hydra_messages:

                    if "only using the -p or -P option" in hydra_error:
                        logging.warning(
                            "Service doesn't need a user wordlist. Restarting the command without it..."
                        )  # pragma: no cover
                    if hydra_error.startswith("[ERROR]"):
                        raise HydraError(hydra_error)

                raise UnknownHydraError(hydra_messages)

    def _userpass_wordlist_string_generator(
        self,
        threads,
        wait_time,
        service,
        port,
        export_type,
        ignore_restore_file,
        userpass_wordlist,
        output_file_name,
    ) -> str:
        """
        Generate the command string when using a userpass wordlist
        """
        hydra_target = f"{service}://{self.ip}:{port}"
        command_string = f"{self.hydra_path} {hydra_target} -w {wait_time}"
        if os.path.isfile(userpass_wordlist):
            command_string += f" {self.hydra_args['UserPassWordlist']} {userpass_wordlist}"
        else:
            raise HydraFileDoesNotExist("Unable to find the file")

        command_string += self._default_string_generator(threads, output_file_name, export_type, ignore_restore_file)

        return command_string

    def _user_and_pass_wordlists_string_generator(
        self,
        threads,
        wait_time,
        service,
        port,
        export_type,
        ignore_restore_file,
        user_wordlist,
        pass_wordlist,
        output_file_name=None,
    ) -> str:
        """Generate the command string when using a users and passwords wordlists"""
        hydra_target = f"{service}://{self.ip}:{port}"
        command_string = f"{self.hydra_path} {hydra_target} -w {wait_time}"

        if str(service) in self.service_without_user:
            logging.info("This service doesn't need a user wordlist, removing it.")
            user_wordlist = None
        else:
            if user_wordlist is not None:
                if os.path.isfile(user_wordlist):
                    command_string = command_string + f" {self.hydra_args['UserWordlist']} {user_wordlist}"
                else:
                    logging.debug(f"Unable to find the file : {user_wordlist}, using it as a username")
                    command_string = command_string + f" {self.hydra_args['Username']} {user_wordlist}"
            else:
                raise HydraNoWordlistGiven("user_wordlist is None")

        if pass_wordlist is not None:
            if os.path.isfile(pass_wordlist):
                command_string = command_string + f" {self.hydra_args['PassWordlist']} {pass_wordlist}"
            else:
                logging.debug(f"Unable to find the file : {pass_wordlist}, using it as a password")
                command_string = command_string + f" {self.hydra_args['Password']} {pass_wordlist}"
        else:
            raise HydraNoWordlistGiven("pass_wordlist is None")

        command_string += self._default_string_generator(threads, output_file_name, export_type, ignore_restore_file)

        return command_string

    def _default_string_generator(self, threads, output_file_name, export_type, ignore_restore_file) -> str:
        """
        Base string generator
        """
        command_string = ""
        if threads is not None:
            command_string = command_string + f" {self.hydra_args['Threads']} {threads}"

        if output_file_name is not None:
            command_string = command_string + f" {self.hydra_args['OutputFilename']} {output_file_name}"

        if export_type is not None:
            command_string = command_string + f" {self.hydra_args['OutputType']} {export_type}"

        if ignore_restore_file is True:
            command_string = command_string + f" {self.hydra_args['IgnoreRestoreFile']}"

        return command_string


if __name__ == "__main__":
    def usage_example():
        ip = "192.168.41.3"
        hydra_object = Hydra(ip)  # Create a Hydra object
        found_credentials = hydra_object.bruteforce(
            "ssh",
            "22",
            "../wordlists/user.txt",
            "../wordlists/pass.txt",
            threads=64,
            ignore_restore_file=True,
            export_type="json",
        )  # Start the bruteforce
        print(f"found credentials :\n{found_credentials}")
    # One line : print(Hydra(ip).bruteforce())
    usage_example()
