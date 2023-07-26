#!/bin/bash
set -e
# -- Config --
VIRTUALENV_DIR=./virtualenv
REQUIREMENTS=./requirements.txt

# -- Execute --
echo "## Install virtualenv to ${VIRTUALENV_DIR} ##"
python3 -m venv ${VIRTUALENV_DIR}

echo "## Activating virtualenv ##"
source ${VIRTUALENV_DIR}/bin/activate

echo "## Installing dependencies (${REQUIREMENTS})"
pip install -r ${REQUIREMENTS}

echo "## Done."

