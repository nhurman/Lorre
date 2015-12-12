import tarfile
import os
import shutil

class NotAByteArrayError(Exception): pass

class ReplayFile:
    read = 'r'
    write = 'w'

    def __init__(self, id, mode, path):
        self._id = id
        self._mode = mode
        self._path = path
        self._fp = None

        if self._mode == ReplayFile.write:
            os.makedirs(os.path.join(self._root_path(), self._chunks_rel_dir()), exist_ok=True)
            os.makedirs(os.path.join(self._root_path(), self._keyframes_rel_dir()), exist_ok=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        if self._fp is not None:
            self._fp.close()
            self._fp = None

        if self._mode == ReplayFile.write:
            # Only save the tar file if the replay is complete
            if os.path.isfile(os.path.join(self._root_path(), self._end_of_game_stats_rel_path())):
                filename = self._archive_path()
                tf = tarfile.open(filename, 'w')
                for filename in os.listdir(self._root_path()):
                    tf.add(os.path.join(self._root_path(), filename), filename)
                tf.close()
            # Delete the files
            shutil.rmtree(self._root_path())

    # --- Helper functions ---
    def _open_archive(self):
        if self._fp is None:
            filename = self._archive_path()
            self._fp = tarfile.open(filename, 'r')
        return self._fp

    def _read_file(self, name):
        try:
            # Read from file
            with open(os.path.join(self._root_path(), name), 'rb') as fp:
                return fp.read()
        except FileNotFoundError:
            # Read from archive
            fp = self._open_archive()
            member = self._fp.getmember(name)
            data = self._fp.extractfile(member)
            return data.read()

    def _write_file(self, name, data):
        if type(data) is str:
            data = data.encode('utf-8')
        if type(data) is not bytes:
            raise NotAByteArrayError()

        # Write to file
        with open(os.path.join(self._root_path(), name), 'wb') as fp:
            fp.write(data)

        """
        # Write to archive
        fp = io.BytesIO(data)
        info = tarfile.TarInfo(name)
        info.size = len(data)
        tf.addfile(info, fp)
        """

    # --- Paths ---
    def _root_path(self):
        return os.path.join(self._path, str(self._id))

    def _archive_path(self):
        return self._root_path() + ".tar"

    def _chunks_rel_dir(self):
        return "chunks"

    def _keyframes_rel_dir(self):
        return "keyframes"

    def _chunk_rel_path(self, id):
        return os.path.join(self._chunks_rel_dir(), str(id))

    def _keyframe_rel_path(self, id):
        return os.path.join(self._keyframes_rel_dir(), str(id))

    def _metadata_rel_path(self):
        return "metadata.json"

    def _last_chunk_info_rel_path(self):
        return "last_chunk_info.json"

    def _end_of_game_stats_rel_path(self):
        return "end_of_game_stats.amf64"

    def _game_rel_path(self):
        return "game.json"

    # --- Write ---
    def write_chunk(self, chunk_id, data):
        self._write_file(self._chunk_rel_path(chunk_id), data)

    def write_keyframe(self, keyframe_id, data):
        self._write_file(self._keyframe_rel_path(keyframe_id), data)

    def write_metadata(self, data):
        self._write_file(self._metadata_rel_path(), data)

    def write_end_of_game_stats(self, data):
        self._write_file(self._end_of_game_stats_rel_path(), data)

    def write_last_chunk_info(self, data):
        self._write_file(self._last_chunk_info_rel_path(), data)

    def write_game(self, data):
        self._write_file(self._game_rel_path(), data)

    # --- Read ---
    def read_chunk(self, chunk_id, data):
        return self._read_file(self._chunk_rel_path(chunk_id))

    def read_keyframe(self, keyframe_id, data):
        return self._read_file(self._keyframe_rel_path(keyframe_id))

    def read_metadata(self, data):
        return self._read_file(self._metadata_rel_path())

    def read_end_of_game_stats(self, data):
        return self._read_file(self._end_of_game_stats_rel_path())

    def read_last_chunk_info(self, data):
        return self._read_file(self._last_chunk_info_rel_path())

    def read_game(self, data):
        return self._read_file(self._game_rel_path())
