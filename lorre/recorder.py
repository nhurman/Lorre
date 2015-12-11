""" League of Legends replay recorder

"""

import os
import json
import time
import urllib.request

class UnknownRegionException(Exception): pass

class Region:
    NA = "NA1"
    EUW = "EUW1"
    EUNE = "EU"

class ReplayServer:
    SPEC_SERVERS = {
        Region.NA: "spectator.na.lol.riotgames.com:8088",
        Region.EUW: "spectator.euw1.lol.riotgames.com:80",
        Region.EUNE: "spectator.eu.lol.riotgames.com:8088"
    }

    def __init__(self, region):
        if region not in self.SPEC_SERVERS:
            raise UnknownRegionException(region)

        self._region = region
        self._baseurl = 'http://{}/observer-mode/rest'.format(self.SPEC_SERVERS[region])

    def featured(self):
        return self._baseurl + '/featured'

    def version(self):
        return self._baseurl + '/version'

    def get_metadata(self, game_id):
        return self._baseurl + '/consumer/getGameMetaData/{}/{}/1/token'.format(
            self._region, game_id)

    def get_last_chunk_info(self, game_id,):
        return self._baseurl + '/consumer/getLastChunkInfo/{}/{}/1/token'.format(
            self._region, game_id)

    def get_keyframe(self, game_id, keyframe_id):
        return self._baseurl + '/consumer/getKeyFrame/{}/{}/{}/token'.format(
            self._region, game_id, keyframe_id)

    def get_chunk(self, game_id, chunk_id):
        return self._baseurl + '/consumer/getGameDataChunk/{}/{}/{}/token'.format(
            self._region, game_id, chunk_id)

    def get_end_of_game_stats(self, game_id):
        return self._baseurl + '/consumer/endOfGameStats/{}/{}/null'.format(
            self._region, game_id)

class GameRecorder:
    def __init__(self, game, region):
        self._game = game
        self._path = os.path.join(os.getcwd(), 'replays', str(game.id))
        self._server = ReplayServer(region)
        self._metadata = None
        self._keyframes = []
        self._chunks = []

        os.makedirs(os.path.join(self._path, 'chunks'), exist_ok=True)
        os.makedirs(os.path.join(self._path, 'keyframes'), exist_ok=True)

    def _get_last_chunk_info(self):
        print("Getting last chunk info")
        url = self._server.get_last_chunk_info(self._game.id)
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)

    def _save_last_chunk_info(self, info):
        print("Saving last chunk info")
        filepath = os.path.join(self._path, "last_chunk_info.json")
        with open(filepath, 'w') as fp:
            data = json.dumps(info)
            print(data, file=fp)

    def _download_metadata(self):
        print("Downloading metadata")
        url = self._server.get_metadata(self._game.id)
        filepath = os.path.join(self._path, "metadata.json")
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            self._metadata = json.loads(data)
            self._metadata['clientBackFetchingEnabled'] = True
            self._metadata['clientBackFetchingFreq'] = 0
            data = json.dumps(self._metadata)
            with open(filepath, 'w') as fp:
                print(data, file=fp)

    def _download_end_of_game_stats(self):
        print("Downloading end of game stats")
        url = self._server.get_end_of_game_stats(self._game.id)
        filepath = os.path.join(self._path, "end_of_game_stats.amf64")
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            with open(filepath, 'w') as fp:
                print(data, file=fp)

    def _download_keyframe(self, keyframe_id):
        print("Downloading keyframe {}".format(keyframe_id))
        keyframe_id = int(keyframe_id)
        url = self._server.get_keyframe(self._game.id, keyframe_id)
        filepath = os.path.join(self._path, 'keyframes', str(keyframe_id))
        urllib.request.urlretrieve(url, filepath)

    def _download_chunk(self, chunk_id):
        print("Downloading chunk {}".format(chunk_id))
        chunk_id = int(chunk_id)
        url = self._server.get_chunk(self._game.id, chunk_id)
        filepath = os.path.join(self._path, 'chunks', str(chunk_id))
        urllib.request.urlretrieve(url, filepath)


    def _write_game_json(self):
        filepath = os.path.join(self._path, "game.json")
        with open(filepath, 'w') as fp:
            print(self._game.to_json(), file=fp)

    def download(self):
        self._write_game_json()
        self._download_metadata()

        #TODO Get spectator server version

        # --- Startup chunks ---
        # Wait for the first chunk to be available
        info = self._get_last_chunk_info()
        while info['chunkId'] <= 0:
            print("Waiting {} for first chunk".format(info['nextAvailableChunk'] / 1000))
            time_to_sleep = max(info['nextAvailableChunk'], 5000)
            time.sleep(time_to_sleep / 1000)
            info = self._get_last_chunk_info()

        # Get the startup chunks if we are ahead
        if info['chunkId'] > info['endStartupChunkId']:
            for chunk_id in range(1, info['endStartupChunkId'] + 1):
                self._download_chunk(chunk_id)

        # --- Current chunks / keyframes ---
        # Start with the chunks of the current keyframe
        # If we are at the beginning of the game there aren't any keyframes available
        current_chunk = info['nextChunkId']
        if current_chunk == 0:
            current_chunk = info['chunkId']

        while current_chunk != info['chunkId']:
            self._download_chunk(current_chunk)
            current_chunk += 1

        # Now we caught up to live, get chunks / keyframes as the arrive
        current_keyframe = 0
        while current_chunk != info['endGameChunkId']:
            # Chunk
            current_chunk = info['chunkId']
            self._download_chunk(current_chunk)

            # Keyframe
            if current_keyframe != info['keyFrameId']:
                current_keyframe = info['keyFrameId']
                self._download_keyframe(current_keyframe)

            # Wait for the next one
            if info['nextAvailableChunk'] > 0:
                time.sleep(info['nextAvailableChunk'] / 1000)
            info = self._get_last_chunk_info()

        # Finally get the metadata + end of game stats
        self._save_last_chunk_info(info)
        self._download_metadata()
        self._download_end_of_game_stats()
