import hashlib
import json
from dataclasses import asdict, dataclass


class RequestRejected(ValueError):
    pass


@dataclass(frozen=True)
class ChallengeRequest:
    request: str
    additional_conditions: str = ''

    def __post_init__(self):
        if not isinstance(self.request, str) or not self.request.strip() or len(self.request) > 4000:
            raise RequestRejected('invalid_request')
        if not isinstance(self.additional_conditions, str) or len(self.additional_conditions) > 2000:
            raise RequestRejected('invalid_conditions')

    def packet(self, run_id, source_ids):
        payload = asdict(self)
        digest = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        return {'schema_version': 'challenge-cli-v1', 'request_id': run_id,
                'conditions_revision': 1, 'input_hash': digest, **payload,
                'available_source_ids': source_ids, 'source_trust': 'untrusted_source_data'}


def pending_result(packet, *, local):
    status = 'agent_unavailable'
    code = 'agent_not_connected'
    message = '에이전트가 연결되지 않아 요청의 처리 범위를 판단하거나 추천을 생성하지 않았습니다.'
    return {'schema_version': 'challenge-cli-v1', 'run_id': packet['request_id'],
            'input_hash': packet['input_hash'], 'status': status, 'code': code,
            'message': message, 'packet': packet, 'recommendations': [],
            'model_requests': 0, 'source_api_requests': 0,
            'execution_mode': 'local_preparation' if local else 'sandbox_preparation',
            'agent_connected': False, 'policy_verification': 'unverified',
            'events': [
                {'seq': 1, 'run_id': packet['request_id'], 'kind': 'result',
                 'name': 'preparation', 'status': status, 'code': code},
            ]}
