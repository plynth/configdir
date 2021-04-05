FROM python:3.9-slim AS base

RUN python -m pip install --upgrade pip

# Python automatically includes libs from PYTHONPATH
ENV PYTHONPATH=/app

FROM base AS poetry
ARG POETRY_VERSION="1.1.5"
# Install poetry into system Python so it does not get in PYTHONPATH
RUN python -m pip install "poetry==$POETRY_VERSION"

FROM poetry AS dependencies
# Install the dependencies into the PYTHONPATH
COPY pyproject.toml poetry.lock /poetry/
WORKDIR /poetry
# Intsall without dependencies because poetry has already listed all of them
RUN poetry export --dev -f requirements.txt | \
  python -m pip install --no-deps --require-hashes -r /dev/stdin --target "$PYTHONPATH"

FROM dependencies AS app

ARG RELEASE

# Install the app into the PYTHONPATH
COPY . /src
WORKDIR /src
RUN rm -f dist/*
RUN poetry version "${RELEASE}"
RUN poetry build -f wheel
# Can't use the same target because pip will completely replace the `bin`
# directory and previsouly installed scripts will be lost. Install to a
# temp directory then copy to $PYTHONPATH.
RUN python -m pip install --no-index --no-deps --target prep dist/*.whl
RUN cp -rlv prep/* "$PYTHONPATH"

FROM base
# Create a minimal image that only has the dependencies and app installed
ENV PATH="${PYTHONPATH}/bin:${PATH}"
COPY --from="app" "$PYTHONPATH" "$PYTHONPATH/"
