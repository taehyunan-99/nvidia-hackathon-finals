"""Bounded JSON collection after the worker has stopped; no model-selected paths."""
import json
import math
import os
import re
import stat


class OutputRejected(ValueError):
    """Only fixed reason codes may cross the API/log boundary."""


def _object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise OutputRejected('duplicate_key')
        value[key] = item
    return value


def _constant(_value):
    raise OutputRejected('non_finite_number')


def _float(raw):
    value = float(raw)
    if not math.isfinite(value):
        raise OutputRejected('non_finite_number')
    return value


def collect_json(root_fd, job_id, *, requester, job_owner, expected_uid,
                 max_bytes=65536):
    """root_fd and job_owner come from the trusted manager, never the payload.

    The manager must stop the writer before collection. This validates the
    transport envelope only; the caller must validate the product result.
    """
    if not isinstance(requester, str) or not requester or requester != job_owner:
        raise OutputRejected('wrong_owner')
    if not isinstance(job_id, str) or not re.fullmatch(r'[a-f0-9]{32}', job_id):
        raise OutputRejected('invalid_job_id')
    if type(max_bytes) is not int or max_bytes < 1:
        raise OutputRejected('invalid_limit')
    directory = file_fd = None
    try:
        directory = os.open(job_id, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                            | os.O_CLOEXEC, dir_fd=root_fd)
        file_fd = os.open('result.json', os.O_RDONLY | os.O_NOFOLLOW
                          | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=directory)
        before = os.fstat(file_fd)
        if not stat.S_ISREG(before.st_mode):
            raise OutputRejected('not_regular')
        if before.st_nlink != 1:
            raise OutputRejected('hardlink')
        if before.st_uid != expected_uid:
            raise OutputRejected('wrong_file_owner')
        if before.st_size > max_bytes:
            raise OutputRejected('too_large')
        chunks, total = [], 0
        while total <= max_bytes:
            chunk = os.read(file_fd, min(8192, max_bytes + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
        if total > max_bytes:
            raise OutputRejected('too_large')
        after = os.fstat(file_fd)
        if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_size, after.st_mtime_ns, after.st_ctime_ns):
            raise OutputRejected('changed_during_read')
        value = json.loads(b''.join(chunks).decode('utf-8'),
                           object_pairs_hook=_object, parse_constant=_constant,
                           parse_float=_float)
        if (not isinstance(value, dict) or set(value) != {'job_id', 'result'}
                or value['job_id'] != job_id or not isinstance(value['result'], dict)):
            raise OutputRejected('invalid_envelope')
        return value['result']
    except OutputRejected:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError):
        raise OutputRejected('unreadable_or_invalid') from None
    finally:
        if file_fd is not None:
            os.close(file_fd)
        if directory is not None:
            os.close(directory)
