# build_pyenv

This CLI tool is a high-performance CLI tool designed to prepare `Python environments for air-gapped or 
restricted-network servers`. It automates the process of downloading, building (if necessary), and caching 
Python packages files(.whl) and their dependencies.

## ✨ Key Features
- `Smart Caching`: Tracks successfully downloaded packages in a .cache_pkg file to skip redundant work.
- `Automatic Build`: If the required package does not provide a `.whl` file, it will build them from source locally and generate the `.whl` file.
- `Detailed Logging`: Separate output.log for full process history and error.log for quick troubleshooting.
- `Modern CLI`: Built with Typer for a polished terminal experience and shell auto-completion.
- `Air-Gap Ready`: Resolves and bundles all sub-dependencies, ensuring your offline installation is complete.


## 🚀 Quick Start

This tool is released as a python package and executable. You need to have `python` and `pip` to install it.

### Build your local environment

As we mentioned before, this tool may build locally the `.whl` files. So if the `OS, CPU architecture or python 
version` of your build environment are not compatible with the target machine, the downloaded or generated `.whl` will 
not be compatible in the target machine. The python version which you use to run the tool will define the downloaded installed

Before build your local environment, check the below things:
- What is the `OS` of your target machine? (e.g. Windows, Linux, MacOS)
- What is the `CPU architecture` of your target machine? (e.g. x86, ARM, etc.)
- What is the `python version` of your target python environment (e.g. 3.11, 3.12, etc.)

For example if you target environment is a `Windows Server 2019` with `x86` CPU and `python 3.11`. Your local environment
should also be `Windows, x86, and python 3.11`.

> We recommend you to use a virtual environment to run the tool.

### Installation

Here we suppose you already have the required `python` and `pip`.

```powershell
pip install build-pyenv
```

### Basic Usage

After installation, you can view all available options of the tool with `build-pyenv.exe --help` 

```powershell
> build-pyenv.exe --help                  
                                                                                                                                                                                                                                                                                                                    
 Usage: build-pyenv [OPTIONS]                                                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                                    
 Main command to download and cache python packages.                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                                    
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *  --requirements        -r      FILE       Path to the requirements.txt file. [required]                                                                                                                                                                                                                        │
│    --output              -o      DIRECTORY  Directory to store downloaded wheels. [default: ./target]                                                                                                                                                                                                            │
│    --logs                -l      PATH       Directory to store log files. [default: ./logs]                                                                                                                                                                                                                      │
│    --install-completion                     Install completion for the current shell.                                                                                                                                                                                                                            │
│    --show-completion                        Show completion for the current shell, to copy it or customize the installation.                                                                                                                                                                                     │
│    --help                                   Show this message and exit.                                                                                                                                                                                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

```

The only required option is `-r`, user must provide a `requirements.txt` file which specifies all the required python
packages. The syntax of the `requirements.txt` is the standard syntax rules defined by **PEP 508**.

For example, if you have a `requirements.txt` like

```text
pandas
numpy
```

When you run the tool, you should see the below outputs
```powershell
(my_test) C:\Users\toto\Documents\tmp>build-pyenv.exe -r requirements.txt
INFO: Logging initialized. Errors -> error.log, All -> output.log
🚀 Starting build process...
INFO: Starting download packages to: C:\Users\toto\Documents\tmp\target
INFO: Processing: pandas...
INFO: [OK] pandas is ready in C:\Users\toto\Documents\tmp\target
INFO: Processing: numpy...
INFO: [OK] numpy is ready in C:\Users\toto\Documents\tmp\target
INFO: Cache updated at C:/Users/toto/Documents/tmp/target/.cache_pkg (Total: 2 packages)
INFO: Wheel files are stored in: C:/Users/toto/Documents/tmp/target/pkgs
INFO: --- All done! ---
✨ Success! Wheels are in C:\Users\toto\Documents\tmp\target
```

> If you don't specify the output dir and log path, the tool will create a default output dir `target`, and 
> a default log dir `logs` in the current directory. 

## 🛠 Workflow for using the output packages

To use the output packages in an `Air-Gapped Server`: 

1. Copy the folder `pkgs` to the target server.
2. In the target server, activate your python virtual environment
3. run `pip install --no-index --find-links ./pkgs -r requirements.txt` 