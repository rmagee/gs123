#!/usr/bin/env bash
# will update all of the requirements files
echo "Updating requirements files..."
pip-compile requirements_test.in -o requirements_test.txt --upgrade
pip-compile requirements_dev.in -o requirements_dev.txt --upgrade
pip-compile requirements.in -o requirements.txt --upgrade
echo "Complete."
