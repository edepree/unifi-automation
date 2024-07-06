# check if the venv module exits; if not, install it
if ! python3 -m venv --help &> /dev/null; then
    echo "> The venv module, which is required, is not installed"
    sudo apt update
    sudo apt install -y python3-venv
fi

# check if the virtual environment exits; if not, create it
if [ ! -d ".venv" ]; then
    echo "> The vitrual environment was not found, creating it"
    python3 -m venv .venv

    # update pip
    python3 -m pip install --upgrade pip
fi

# activate a virtual environment
source .venv/bin/activate

# install python dependencies
pip3 install -r requirements.txt
