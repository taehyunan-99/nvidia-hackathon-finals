import hashlib
import json
import os
import re
import stat
from pathlib import Path, PurePosixPath


class FileRejected(ValueError):
    pass


MAX_FILE_BYTES = 65536
MAX_TOTAL_BYTES = 1048576
MAX_FILES = 128
MAX_ENTRIES = 512
SUFFIXES = {'.md', '.txt', '.csv', '.json'}


def root_fd(path, *, metadata_only=False):
    if os.name != 'posix' or not hasattr(os, 'O_NOFOLLOW') or not hasattr(os, 'O_PATH'):
        raise FileRejected('linux_file_boundary_required')
    path = Path(path)
    if not path.is_absolute() or '..' in path.parts:
        raise FileRejected('invalid_root')
    fd = os.open('/', os.O_PATH | os.O_DIRECTORY | os.O_CLOEXEC)
    try:
        for index, part in enumerate(path.parts[1:], start=1):
            access = os.O_PATH if metadata_only or index < len(path.parts) - 1 else os.O_RDONLY
            child = os.open(part, access | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=fd)
            os.close(fd)
            fd = child
        return fd
    except OSError:
        os.close(fd)
        raise FileRejected('unavailable_root') from None


def bounded_names(directory):
    names = []
    with os.scandir(directory) as items:
        for item in items:
            names.append(item.name)
            if len(names) > MAX_ENTRIES:
                raise FileRejected('input_inventory_limit')
    return names


def source_parts(source_id):
    if (not isinstance(source_id, str) or not source_id or len(source_id) > 240
            or '\\' in source_id or ':' in source_id or '\x00' in source_id):
        raise FileRejected('invalid_source_id')
    parts = source_id.split('/')
    if any(part in {'', '.', '..'} for part in parts) or len(parts) > 8:
        raise FileRejected('invalid_source_id')
    if PurePosixPath(source_id).suffix not in SUFFIXES:
        raise FileRejected('unsupported_source')
    return parts


class InputFiles:
    def __init__(self, root, *, metadata_only=False):
        self.fd = root_fd(root, metadata_only=metadata_only)

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None

    def paths(self):
        if self.fd is None:
            raise FileRejected('input_closed')
        found, entries = [], [0]

        def visit(directory, prefix):
            names = bounded_names(directory)
            entries[0] += len(names)
            if entries[0] > MAX_ENTRIES:
                raise FileRejected('input_inventory_limit')
            for name in sorted(names):
                if name.startswith('.'):
                    continue
                path = '/'.join([*prefix, name])
                item = os.stat(name, dir_fd=directory, follow_symlinks=False)
                if stat.S_ISDIR(item.st_mode):
                    if len(prefix) >= 7:
                        raise FileRejected('input_depth_limit')
                    child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                    dir_fd=directory)
                    try:
                        visit(child, [*prefix, name])
                    finally:
                        os.close(child)
                elif (stat.S_ISREG(item.st_mode) and item.st_nlink == 1
                      and PurePosixPath(name).suffix in SUFFIXES):
                    source_parts(path)
                    found.append(path)
                    if len(found) > MAX_FILES:
                        raise FileRejected('input_inventory_limit')

        try:
            visit(self.fd, [])
        except OSError:
            raise FileRejected('input_unavailable') from None
        return found

    def read(self, source_id):
        parts = source_parts(source_id)
        if self.fd is None:
            raise FileRejected('input_closed')
        directory = os.dup(self.fd)
        file = None
        try:
            for part in parts[:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                dir_fd=directory)
                os.close(directory)
                directory = child
            file = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC,
                           dir_fd=directory)
            before = os.fstat(file)
            if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
                raise FileRejected('invalid_source_file')
            if before.st_size > MAX_FILE_BYTES:
                raise FileRejected('source_too_large')
            chunks, size = [], 0
            while size <= MAX_FILE_BYTES:
                chunk = os.read(file, min(8192, MAX_FILE_BYTES + 1 - size))
                if not chunk:
                    break
                chunks.append(chunk)
                size += len(chunk)
            after = os.fstat(file)
            if size > MAX_FILE_BYTES:
                raise FileRejected('source_too_large')
            if (before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
                    after.st_size, after.st_mtime_ns, after.st_ctime_ns):
                raise FileRejected('source_changed')
            raw = b''.join(chunks)
            if b'\x00' in raw:
                raise FileRejected('invalid_source_text')
            return {'source_id': source_id, 'sha256': hashlib.sha256(raw).hexdigest(),
                    'text': raw.decode('utf-8'), 'bytes': len(raw), 'trust': 'untrusted_source_data'}
        except (OSError, UnicodeError):
            raise FileRejected('source_unavailable') from None
        finally:
            if file is not None:
                os.close(file)
            os.close(directory)

    def search(self, query, offset=0):
        if (not isinstance(query, str) or len(query) > 240 or type(offset) is not int
                or offset < 0 or offset > MAX_FILES):
            raise FileRejected('invalid_search')
        matches, skipped, total = [], 0, 0
        for path in self.paths():
            try:
                doc = self.read(path)
            except FileRejected:
                skipped += 1
                continue
            total += doc['bytes']
            if total > MAX_TOTAL_BYTES:
                raise FileRejected('input_byte_limit')
            index = doc['text'].casefold().find(query.casefold())
            if index >= 0 or query.casefold() in path.casefold():
                start = max(0, index - 80)
                matches.append({'source_id': path, 'sha256': doc['sha256'],
                                'excerpt': doc['text'][start:start + 320]})
        page = matches[offset:offset + 10]
        return {'status': 'ok' if page else 'empty', 'matches': page, 'total_matches': len(matches),
                'next_offset': offset + 10 if offset + 10 < len(matches) else None,
                'skipped_files': skipped, 'trust': 'untrusted_source_data'}


def read_task(root):
    files = InputFiles(root, metadata_only=True)
    try:
        return files.read('TASK.md')
    finally:
        files.close()


def write_result(root, run_id, result):
    if not isinstance(run_id, str) or not re.fullmatch(r'[a-f0-9]{32}', run_id):
        raise FileRejected('invalid_run_id')
    raw = json.dumps({'job_id': run_id, 'result': result}, ensure_ascii=False, allow_nan=False).encode('utf-8')
    if len(raw) > MAX_FILE_BYTES:
        raise FileRejected('output_too_large')
    root_directory = root_fd(root)
    directory = file = None
    try:
        os.mkdir(run_id, mode=0o700, dir_fd=root_directory)
        directory = os.open(run_id, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                            dir_fd=root_directory)
        file = os.open('result.tmp', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                       0o600, dir_fd=directory)
        with os.fdopen(file, 'wb') as stream:
            file = None
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.rename('result.tmp', 'result.json', src_dir_fd=directory, dst_dir_fd=directory)
        os.fsync(directory)
        return str(Path(root) / run_id / 'result.json')
    except OSError:
        raise FileRejected('output_write_failed') from None
    finally:
        if file is not None:
            os.close(file)
        if directory is not None:
            os.close(directory)
        os.close(root_directory)
