ARG BASE_IMAGE=python:3.12-slim@sha256:05cda9777409a9c3ffddd94a4c476b79f0769a0b4857f0c7ed9226b6800b0d6f
FROM ${BASE_IMAGE}
USER root
WORKDIR /opt/family-minimum
ENV FAMILY_PROJECT_ROOT=/opt/family-minimum
COPY agent /opt/family-minimum/agent
COPY scripts/model_policy.py scripts/probe_family_sources.py /opt/family-minimum/scripts/
COPY scripts/openshell_harness/probe.py /opt/family-minimum/scripts/policy_probe.py
COPY docs/playbooks/model-policy.json /opt/family-minimum/docs/playbooks/model-policy.json
COPY docs/catalog/contracts/family-v1.schema.json docs/catalog/contracts/family-v1.cases.json /opt/family-minimum/docs/catalog/contracts/
RUN pip install --no-cache-dir ./agent
RUN mkdir -p /hackathon/input /hackathon/output /hackathon/restricted /hackathon/secrets \
    && printf 'PUBLIC_CONTROL\n' > /hackathon/input/control.txt \
    && python -c "import secrets,pathlib; [pathlib.Path('/hackathon/'+p+'/control.txt').write_text(secrets.token_hex(32)) for p in ['restricted','secrets']]" \
    && ln -sfn /hackathon/restricted/control.txt /hackathon/output/link-restricted \
    && ln -sfn /hackathon/secrets/control.txt /hackathon/output/link-secrets \
    && chown -R 1000:1000 /hackathon && chmod 644 /hackathon/*/control.txt
USER 1000:1000
WORKDIR /hackathon/output
CMD ["sleep", "infinity"]
