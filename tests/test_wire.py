"""Exercise a released Goose binary against a local server; no live credentials."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

requests = []
get_requests = []
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        get_requests.append(self.path)
        self.send_error(404)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        requests.append((self.path, dict(self.headers), body))
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.end_headers()
        def event(delta, finish=None):
            obj = {'id': 'chatcmpl-wire', 'object': 'chat.completion.chunk',
                   'created': 1, 'model': 'qwen/qwen3.8-27b',
                   'choices': [{'index': 0, 'delta': delta, 'finish_reason': finish}]}
            self.wfile.write(('data: ' + json.dumps(obj) + '\n\n').encode())
        is_main = any(m.get('role') == 'user' and str(m.get('content', '')).startswith('Run the synthetic') for m in body['messages'])
        has_tool = any(m.get('role') == 'tool' for m in body['messages'])
        if is_main and not has_tool:
            event({'role': 'assistant', 'reasoning': 'I will use the test tool.'})
            event({'tool_calls': [{'index': 0, 'id': 'call_wire', 'type': 'function',
                  'function': {'name': 'shell', 'arguments': '{"command":"printf GOOSE_WIRE_OK"}'}}]})
            event({}, 'tool_calls')
        else:
            event({'role': 'assistant', 'content': 'GOOSE_WIRE_OK'})
            event({}, 'stop')
        self.wfile.write(b'data: [DONE]\n\n')
        self.wfile.flush()

server = HTTPServer(('127.0.0.1', 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
with tempfile.TemporaryDirectory(prefix='fortytwo-goose-wire-') as temporary:
    root = Path(temporary)
    config = root / 'config/custom_providers'
    config.mkdir(parents=True)
    candidate = json.loads((Path(__file__).resolve().parents[1] / 'fortytwo.json').read_text())
    candidate['base_url'] = f'http://127.0.0.1:{server.server_port}/v1/chat/completions'
    (config / 'fortytwo.json').write_text(json.dumps(candidate))
    env = {k: v for k, v in os.environ.items()
           if not k.startswith(('GOOSE_', 'LANGFUSE_', 'OTEL_', 'FORTYTWO_'))}
    env.update(GOOSE_PATH_ROOT=str(root), GOOSE_DISABLE_KEYRING='1',
               GOOSE_MODE='auto', FORTYTWO_API_KEY='local-dummy-key')
    run = subprocess.run([sys.argv[1], 'run', '--no-profile', '--no-session',
                          '--with-builtin', 'developer', '--provider', 'fortytwo',
                          '--model', 'qwen/qwen3.8-27b', '--max-turns', '2',
                          '--output-format', 'stream-json', '--text',
                          'Run the synthetic test tool and report its result.'],
                         cwd=root, env=env, capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stderr
    assert not get_requests, f'Unexpected discovery requests: {get_requests}'
    main_requests = [r for r in requests if any(m.get('role') == 'user' and str(m.get('content', '')).startswith('Run the synthetic') for m in r[2]['messages'])]
    assert len(main_requests) == 2, f'Expected a tool round trip: {len(main_requests)} requests'
    for path, headers, body in requests:
        assert path == '/v1/chat/completions', path
        headers = {k.lower(): v for k, v in headers.items()}
        assert headers['authorization'] == 'Bearer local-dummy-key'
        for key, value in candidate['headers'].items():
            assert headers[key] == value
        assert headers.get('agent-session-id')
        assert body['model'] == 'qwen/qwen3.8-27b'
        assert body['stream'] is True
    history = main_requests[1][2]['messages']
    assert any(m.get('role') == 'assistant' and
               'I will use the test tool.' in m.get('reasoning_content', '') for m in history)
    assert any(m.get('role') == 'tool' and m.get('tool_call_id') == 'call_wire' and
               'GOOSE_WIRE_OK' in str(m.get('content')) for m in history)
    events = [json.loads(line) for line in run.stdout.splitlines() if line.startswith('{')]
    assert any(e.get('type') == 'complete' for e in events)
    print('PASS: released Goose parses provider; endpoint, static model, streaming, headers, '
          'session ID, tool execution/result IDs and thinking replay verified across two requests')
server.shutdown()
