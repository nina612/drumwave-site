#!/usr/bin/env python3
"""Static server for this folder, used by the "sept-8-direct" launch config.

    python3 serve-sept8.py [port]        # default 8124

`python3 -m http.server` would be the obvious thing here, but it cannot start
under the preview launcher: that module builds its argument parser with
`default=os.getcwd()`, and the launcher spawns the server from a directory it
is not permitted to stat, so the call raises PermissionError before any
argument is read. Pinning the directory explicitly avoids ever asking for the
process's cwd, and serving this folder directly means edits to sept-8.html are
live on reload with no copy step.
"""

import functools
import http.server
import os
import socketserver
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8124


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == '__main__':
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    with Server(('127.0.0.1', PORT), handler) as httpd:
        print('Serving %s at http://localhost:%d' % (ROOT, PORT))
        httpd.serve_forever()
