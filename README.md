# Py-Hydra

Py-Hydra, a python interface for [THC-Hydra](https://github.com/vanhauser-thc/thc-hydra), it allows to bruteforce network services using python through the power of Hydra.
Please refer to the Hydra's GitHub for any question regarding the legal use of this software : [Hydra Github](https://github.com/vanhauser-thc/thc-hydra) 

## Getting Started
### Prerequisites

This project requires you to have Hydra and Python installed: 
- [Hydra](https://github.com/vanhauser-thc/thc-hydra)
- [Python](https://www.python.org/downloads/)

### Installing

Developed and tested on python3.8 & 3.10
 
Installing Hydra and Python

    sudo apt install hydra python3
    git clone https://github.com/knock-knock-cyber/Py-Hydra
    cd Py-Hydra

## How to use

Here's a code example on how to bruteforce using Py-Hydra.

    from pyhydra import Hydra

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

The docstring under the bruteforce method also contains the supported Hydra commands.
This method will either return an empty dictionary (which means that no credentials were found) or a dictionary with the working credentials.


## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) to know how to contribute to his project.

## Authors

  - **Knock Knock** : Developer team

## License

This project is licensed under the [GNU GPLv3](LICENSE) see the [LICENSE](LICENSE) file for details.

## Sponsor this project

[Get us a coffee](https://www.buymeacoffee.com/knockknockcyber)