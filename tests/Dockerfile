# NOTE: This dockerfile should only be used for internal testing purposes
# and should not form the basis of an official image pushed out
# to a registry
ARG PYTHON_VERSION=3.10
ARG OS_DISTRO=slim-bullseye

FROM python:${PYTHON_VERSION}-${OS_DISTRO}

# These are are own build args recorded as env variables
ARG OS_DISTRO
ENV OS_DISTRO=${OS_DISTRO}
ENV PYRIGHT_USER_ID=9999

# These are provided by Docker
ARG BUILDPLATFORM
ARG BUILDOS
ARG BUILDARCH
ARG BUILDVARIANT
ARG TARGETPLATFORM
ARG TARGETOS
ARG TARGETARCH

ENV DOCKER_BUILDPLATFORM=${BUILDPLATFORM}
ENV DOCKER_BUILDOS=${BUILDOS}
ENV DOCKER_BUILDARCH=${BUILDARCH}
ENV DOCKER_BUILDVARIANT=${BUILDVARIANT}
ENV DOCKER_TARGETPLATFORM=${TARGETPLATFORM}
ENV DOCKER_TARGETOS=${TARGETOS}
ENV DOCKER_TARGETARCH=${TARGETARCH}

# TODO: Using the slim variant is a bit hackier. Better to
# cat and grep /etc/*release*. Also, the [[ ]] command
# is a bash thing so thats why we subshell for the test
RUN \
    if [[ $OS_DISTRO =~ alpine ]]; then \
      adduser -u ${PYRIGHT_USER_ID} -D pyright; \
      apk add gcc musl-dev yaml-dev yaml libffi-dev; \
    elif bash -c "[[ ${OS_DISTRO} =~ slim ]]"; then \
      useradd --create-home --uid ${PYRIGHT_USER_ID} --shell /bin/bash pyright; \
    else \
      echo "Unrecognized distro $OS_DISTRO"; \
      exit 99; \
    fi

USER pyright
WORKDIR /home/pyright/pyright-python
ENV PATH="/home/pyright/.local/bin:${PATH}"

COPY --chown=pyright:pyright . .

RUN pip install --upgrade pip && \
    pip install .[dev]

ENV PYRIGHT_PYTHON_DEBUG="1"

# This has the side-effect of downing the node binaries
# and will fail if the CLI cannot be ran
RUN pyright --version

# Run the unit tests to ensure they pass in an environment without Node present globally
RUN tox -e py
