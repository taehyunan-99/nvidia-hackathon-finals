ARG BASE_IMAGE=finals-family-agent:runtime
FROM ${BASE_IMAGE}
USER root
COPY agent /opt/family-minimum/agent
RUN pip install --no-deps --no-cache-dir /opt/family-minimum/agent
USER 1000:1000
