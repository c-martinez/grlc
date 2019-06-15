#!/bin/bash

if [[ $TRAVIS_OS_NAME == 'osx' ]]; then
  pyenv local $PYENV_VERSION
  if [[ $PYENV_VERSION == 2* ]]; then
    alias pip=pip2
  fi
  if [[ $PYENV_VERSION == 3* ]]; then
    alias pip=pip3
  fi
fi

if [[ $TRAVIS_BUILD_STAGE_NAME == 'Deploy' ]]; then
  virtualenv venv -p python$PYENV_VERSION
  source venv/bin/activate
fi
echo "Python version"
python --version

echo "Pip version"
pip --version


# Horrible hack -- but we should remove pythonql functionality soon anyway...
pip install pythonql3
echo "Install dot"
pip install .

echo "Install test requirements"
pip install -r requirements-test.txt
