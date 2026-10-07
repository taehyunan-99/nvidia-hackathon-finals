FROM ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55
RUN apt-get update && apt-get install -y --no-install-recommends python3 ca-certificates iproute2 nftables && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/harness /hackathon/input /hackathon/output /hackathon/restricted /hackathon/secrets \
    && printf 'PUBLIC_CONTROL\n' > /hackathon/input/control.txt \
    && printf 'SYNTHETIC_NOT_A_SECRET\n' > /hackathon/restricted/control.txt \
    && printf 'SYNTHETIC_NOT_A_SECRET\n' > /hackathon/secrets/control.txt \
    && ln -s /hackathon/restricted/control.txt /hackathon/output/link-restricted \
    && ln -s /hackathon/secrets/control.txt /hackathon/output/link-secrets \
    && chown -R 1000:1000 /hackathon && chmod 644 /hackathon/*/control.txt
COPY probe.py /opt/harness/probe.py
USER 1000:1000
WORKDIR /hackathon/output
CMD ["sleep", "infinity"]
