FROM ubuntu:24.04@sha256:534baea6a22c03a63003dbc8dbe78fe34bc0d7e595d9a9dc9834884ff530eb55
RUN apt-get update && apt-get install -y --no-install-recommends python3 ca-certificates && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /opt/bridge /hackathon/input /hackathon/output /hackathon/restricted /hackathon/secrets \
    && printf 'PUBLIC_CONTROL\n' > /hackathon/input/control.txt \
    && python3 -c "import secrets,pathlib; [pathlib.Path('/hackathon/'+p+'/control.txt').write_text(secrets.token_hex(32)) for p in ['restricted','secrets']]" \
    && chmod 644 /hackathon/*/control.txt && chown -R 1000:1000 /hackathon
COPY worker.py /opt/bridge/worker.py
USER 1000:1000
WORKDIR /hackathon/output
CMD ["sleep", "infinity"]
