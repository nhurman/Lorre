import http.server
import re
import os
import json
from .replay import  ReplayFile

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
        self.send_header('Content-type', content_type)
        self.end_headers()

        if type(data) is str:
            data = bytes(data, 'UTF-8')
        self.wfile.write(data)

    def do_POST(self):
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
        if args['method'] == 'end':
            # Riot pls
            self.send_error(405)
            return

        self.send_error(404)

    def do_GET(self):
        if self.path == '/':
            return self.do_index()
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
            rf = ReplayFile(args['gameid'], ReplayFile.read, REPLAYS_DIR)

            if args['method'] == 'getGameMetaData':
                try:
                    self.write_200('application/octet-stream', rf.read_metadata())
                except FileNotFoundError:
                    self.send_error(404)
                return
            elif args['method'] == 'getLastChunkInfo':
                try:
                    self.write_200('application/octet-stream', rf.read_last_chunk_info())
                except FileNotFoundError:
                    self.send_error(404)
                return
            elif args['method'] == 'getKeyFrame':
                try:
                    self.write_200('application/octet-stream', rf.read_keyframe(args['id']))
                except FileNotFoundError:
                    self.send_error(404)
                return
            elif args['method'] == 'getGameDataChunk':
                try:
                    self.write_200('application/octet-stream', rf.read_chunk(args['id']))
                except FileNotFoundError:
                    self.send_error(404)
                return
            elif args['method'] == 'endOfGameStats':
                try:
                    self.write_200('application/octet-stream', rf.read_end_of_game_stats())
                except FileNotFoundError:
                    self.send_error(404)
                return
            else:
                self.send_error(404)
                return

    def do_index(self):
        self.send_response(200, 'OK')
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        for game in os.listdir(REPLAYS_DIR):
            if game.endswith(".tar"):
                game = game[:-4]
            try:
                game_id = int(game)
            except ValueError:
                continue

            rf = ReplayFile(game_id, ReplayFile.read, REPLAYS_DIR)
            game_json = json.loads(rf.read_game().decode('utf-8'))
            key = game_json['observers']['encryptionKey']
            platform = game_json['platformId']

            r = 'replay' if rf.is_finished() and not rf.is_partial() else 'spectator'
            h = 'localhost:8080'
            self.wfile.write("{} {} {} {} {}\n".format(r, h, key, game_id, platform).encode("utf-8"))