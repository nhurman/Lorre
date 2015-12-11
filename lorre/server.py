import http.server
import re
import os
import json

VERSION = '1.82.98'
REPLAYS_DIR = 'replays'
class ReplayServer(http.server.HTTPServer):
    def __init__(self):
        http.server.HTTPServer.__init__(self, ('', 8080), RequestHandler)

    def run(self):
        self.serve_forever()


class RequestHandler(http.server.BaseHTTPRequestHandler):
    def write_200(self, content_type, data):
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'content_type')
        self.end_headers()

        if type(data) is str:
            data = bytes(data, 'UTF-8')
        self.wfile.write(data)

    def do_GET(self):
        print('GET Request', self.path)
        if self.path == '/observer-mode/rest/consumer/version':
            self.write_200('text/plain', VERSION)
        elif self.path == '/observer-mode/rest/featured':
            self.write_200('application/json', '{"gameList":[], "clientRefreshInterval":300}')
        else:
            r = re.compile('^/observer-mode/rest/consumer'
                + '/(?P<method>[a-zA-Z]+)'
                + '/(?P<region>[A-Z1-9]+)'
                + '/(?P<gameid>[0-9]+)'
                + '/(?:null|(?P<id>-?[0-9]+)/token)'
                + '$')

            m = r.match(self.path)
            if m is None:
                self.send_error(404)
                return

            args = m.groupdict()
            if args['method'] == 'getGameMetaData':
                try:
                    f = open(os.path.join(REPLAYS_DIR, args['gameid'], 'metadata.json'), 'rb')
                    self.write_200('application/octet-stream', f.read())
                except FileNotFoundError:
                    self.send_error(404)
                return
            elif args['method'] == 'getLastChunkInfo':
                try:
                    f = open(os.path.join(REPLAYS_DIR, args['gameid'], 'last_chunk_info.json'), 'rb')
                    self.write_200('application/octet-stream', f.read())
                    return
                except FileNotFoundError:
                    self.send_error(404)
                return
            elif args['method'] == 'getKeyFrame':
                try:
                    f = open(os.path.join(REPLAYS_DIR, args['gameid'], 'keyframes', args['id']), 'rb')
                    self.write_200('application/octet-stream', f.read())
                    return
                except FileNotFoundError:
                    self.send_error(404)
                return
            elif args['method'] == 'getGameDataChunk':
                try:
                    f = open(os.path.join(REPLAYS_DIR, args['gameid'], 'chunks', args['id']), 'rb')
                    self.write_200('application/octet-stream', f.read())
                    return
                except FileNotFoundError:
                    self.send_error(404)
                return
            elif args['method'] == 'endOfGameStats':
                try:
                    f = open(os.path.join(REPLAYS_DIR, args['gameid'], 'end_of_game_stats.amf64'), 'rb')
                    self.write_200('application/octet-stream', f.read())
                    return
                except FileNotFoundError:
                    self.send_error(404)
                return
            else:
                self.send_error(404)
                return
