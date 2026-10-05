"""Local static preview that does not serve credentials or directory listings."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class PreviewHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = PurePosixPath(unquote(urlsplit(self.path).path))
        hidden = any(part.startswith('.') for part in path.parts)
        assets = path.parts[:5] == ('/', '.agents', 'skills', 'nvidia-ui', 'assets')
        if '..' in path.parts or (hidden and not assets):
            self.send_error(404)
            return None
        return super().send_head()

    def list_directory(self, path):
        self.send_error(404)
        return None


if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 8765), partial(PreviewHandler, directory=str(ROOT)))
    print('Preview: http://127.0.0.1:8765/design/agent-flow.html', flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
