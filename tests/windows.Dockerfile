# NOTE: This dockerfile should only be used for internal testing purposes
# and should not form the basis of an official image pushed out
# to a registry

FROM winamd64/python:3.10

WORKDIR /home/runner/pyright-python

# https://github.com/docker-library/python/issues/359
RUN certutil -generateSSTFromWU roots.sst; certutil -addstore -f root roots.sst;  del roots.sst

COPY . .

RUN pip install .
RUN pip install -U -r dev-requirements.txt

# This has the side-effect of downing the node binaries
# and will fail if the CLI cannot be ran
RUN pyright --version

# Run the unit tests to ensure they pass in an environment without Node present globally
RUN tox -e py
