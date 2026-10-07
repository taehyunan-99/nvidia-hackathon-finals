# Build with a separate context containing only the complete hackathon package.
ARG BASE_IMAGE=finals-family-agent:runtime
FROM ${BASE_IMAGE}
USER root
COPY hackathon /hackathon
RUN chown -R 1000:1000 /hackathon
USER 1000:1000
