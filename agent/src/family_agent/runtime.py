import json
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from family_minimum.runtime import Runtime
from .contracts import assess, check, validator
from .sources import SeoulSources, now


class Decision(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    action: Literal['finish_results', 'finish_hold', 'finish_no_candidates', 'finish_limited', 'finish_failed', 'ask_user']
    candidate_ids: list[str] = Field(max_length=5)
    question_field: Literal['grade', 'guardians', 'visit_date', 'delivery_mode'] | None = None
    reason: str = Field(min_length=1, max_length=500)


class FamilyRuntime(Runtime):
    def __init__(self, ledger, model, key, conditions, request_id, revision=1,
                 implementation=None, sources=None, **kwargs):
        super().__init__(ledger, model, key, **kwargs)
        self.conditions = check('conditions', conditions)
        check('search_input', {'request_id': request_id, 'conditions_revision': revision, 'conditions': conditions, 'cursor': None, 'page_size': 5})
        self.request_id, self.revision, self.as_of = request_id, revision, now()
        self.implementation = None if implementation is False else implementation if implementation is not None else validator()
        self.sources = sources or SeoulSources(request_id, revision, conditions)
        self.details, self.assessments, self.tool_cache, self.failures = {}, {}, {}, []
        self.search_result, self.tool_steps = None, 0

    def tool(self, name, argument=None):
        with self.lock:
            if self.closed or self.steps >= self.policy.max_steps:
                raise ValueError('run_closed_or_step_limit')
            self.budget._wait(0)
            self.tool_steps += 1
            if self.tool_steps > self.policy.max_steps:
                raise ValueError('tool_step_limit')
            cache_key = (name, argument)
            if cache_key in self.tool_cache:
                self.events.append({'kind': 'tool', 'name': name, 'status': 'cached'})
                return self.tool_cache[cache_key]
            if name == 'search_experiences':
                result = check('search_output', self.sources.search(argument))
                self.search_result = result
                result = {**result, 'summaries': self.sources.summaries()}
            elif name in ('get_experience_detail', 'read_official_source'):
                cid = argument.removeprefix('official:') if name == 'read_official_source' else argument
                if cid not in self.sources.rows:
                    raise ValueError('unobserved_candidate')
                if name == 'read_official_source' and (argument != 'official:' + cid or cid not in self.details):
                    raise ValueError('unobserved_source')
                result = check('detail_output', self.sources.detail(cid, official=name == 'read_official_source'))
                if result['status'] == 'ok':
                    parts = self.details.setdefault(cid, {})
                    parts[result['source_id']] = result
                    payload = {'schema_version': 'family-v1', 'request_id': self.request_id,
                        'conditions_revision': self.revision, 'as_of': self.as_of, 'conditions': self.conditions,
                        'candidate_id': cid, 'trusted_source_ids': list(parts),
                        'evidence': [e for part in parts.values() for e in part['evidence']],
                        'facts': [f for part in parts.values() for f in part['facts']]}
                    self.assessments[cid] = assess(payload, self.implementation)
                    result = {**result, 'validation': self.assessments[cid],
                        'validator_connected': self.implementation is not None,
                        'official_source_id': 'official:' + cid}
            elif name == 'validate_candidate':
                if argument not in self.assessments: raise ValueError('detail_required')
                result = self.assessments[argument]
            else:
                raise ValueError('unknown_tool')
            if result.get('status') in ('error', 'policy_denied'):
                self.failures.append({'tool': name, 'candidate_id': argument, 'error_code': result.get('error_code')})
            self.events.append({'kind': 'tool', 'name': name, 'status': result.get('status', result.get('overall')),
                'candidate_id': argument, 'source_ids': [result['source_id']] if 'source_id' in result else []})
            if 'validation' in result:
                self.events.append({'kind': 'validation', 'candidate_id': cid,
                    'status': result['validation']['overall'], 'validator_connected': self.implementation is not None})
            self.tool_cache[cache_key] = result
            return result

    def question(self, field):
        needs = [n for a in self.assessments.values() for n in a['needs'] if n['kind'] == 'user_input']
        allowed = {'grade': 'grade', 'guardians': 'companions', 'visit_date': 'visit_date', 'delivery_mode': 'delivery'}
        if not any(n['field'] == allowed[field] for n in needs):
            raise ValueError('question_without_observed_need')
        options = {'grade': [(str(i), f'초등 {i}학년') for i in range(1, 7)] + [('preschool', '미취학'), ('teen', '중·고등학생')],
            'guardians': [('guardians-0', '0명'), ('guardians-1', '1명'), ('guardians-2plus', '2명 이상')],
            'delivery_mode': [('in_person', '대면'), ('online', '온라인')]}
        if field == 'visit_date':
            # Arbitrary dates cannot be encoded as a guessed pair of choices.
            raise ValueError('edit_date_card_required')
        members = self.conditions['children'] or []
        member = next((c['member_id'] for c in members if c['grade'] is None), None) if field == 'grade' else None
        if field == 'grade' and (not members or member is None):
            raise ValueError('edit_family_cards_required')
        return check('question_card', {'question_id': f'q-{self.revision}-{field}', 'request_id': self.request_id,
            'conditions_revision': self.revision, 'field': field, 'member_id': member,
            'options': [{'id': key, 'label': label} for key, label in options[field]]})

    def finish(self, action, selected, reason, question=None):
        cards = []
        for cid, assessment in self.assessments.items():
            cards.append({**self.sources.card(cid), 'validation': assessment,
                'evidence': [e for part in self.details[cid].values() for e in part['evidence']],
                'selected': cid in selected})
        self.events.append({'kind': 'result', 'status': action, 'reason': reason})
        return {'schema_version': 'family-agent-v1', 'request_id': self.request_id,
            'conditions_revision': self.revision, 'conditions': self.conditions,
            'mode': 'live', 'action': action, 'reason': reason, 'question': question,
            'candidates': cards, 'scope': self.search_result['scope'] if self.search_result else None,
            'failures': self.failures, 'validator_connected': self.implementation is not None,
            'events': self.events, 'physical_model_requests': self.budget.count,
            'source_requests': self.sources.calls, 'availability': 'unverified'}

    def validate(self, text):
        decision = Decision.model_validate_json(text)
        if self.search_result is None: raise ValueError('search_required')
        if len(set(decision.candidate_ids)) != len(decision.candidate_ids): raise ValueError('duplicate_selection')
        for cid in decision.candidate_ids:
            if cid not in self.assessments or self.assessments[cid]['overall'] == 'unsuitable':
                raise ValueError('unverified_or_unsuitable_selection')
        if decision.action == 'finish_results':
            if not decision.candidate_ids or any(self.assessments[c]['overall'] != 'suitable' for c in decision.candidate_ids):
                raise ValueError('unverified_recommendation')
            if self.failures: raise ValueError('partial_failure_requires_hold')
        if decision.action == 'finish_no_candidates':
            scope = self.search_result['scope']
            if self.search_result['status'] not in ('ok', 'empty') or scope['coverage'] != 'complete_for_query' or scope['limit_reached']:
                raise ValueError('incomplete_search_not_empty')
            if any(c not in self.assessments or self.assessments[c]['overall'] != 'unsuitable'
                   for c in self.search_result['candidate_ids']): raise ValueError('unchecked_candidates')
        question = self.question(decision.question_field) if decision.action == 'ask_user' and decision.question_field else None
        if decision.action == 'ask_user' and question is None: raise ValueError('missing_question')
        if decision.action != 'ask_user' and decision.question_field: raise ValueError('unexpected_question')
        return self.finish(decision.action, decision.candidate_ids, decision.reason, question)

    def failed(self, error_code):
        self.failures.append({'tool': 'agent_execution', 'candidate_id': None, 'error_code': error_code})
        return self.finish('finish_hold' if self.assessments else 'finish_failed', [], 'execution_failed:' + error_code)

    def limited(self, reason):
        return self.finish('finish_limited', [], reason)
