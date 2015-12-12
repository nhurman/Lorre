import cassiopeia.riotapi
from cassiopeia.type.api.exception import APIError
from cassiopeia.type.core.common import LoadPolicy
from lorre import recorder
from lorre import server
import time

if __name__ == '__main__':
    cassiopeia.riotapi.set_load_policy(LoadPolicy.lazy);
    cassiopeia.riotapi.set_region("EUW")
    cassiopeia.riotapi.set_api_key("")

    summoner_name = 'I Haxa I'
    summoner = None

    while True:
        if True:
            try:
                if summoner is None:
                    summoner = cassiopeia.riotapi.get_summoner_by_name(summoner_name)
                game = summoner.current_game()
            except APIError:
                continue
        else:
            featured = cassiopeia.riotapi.get_featured_games()
            game = featured[0]

        if game is None:
            print("Game not found, waiting 3 minutes")
            time.sleep(180)
        else:
            rec = recorder.GameRecorder(game, recorder.Region.EUW)
            rec.download()

else:
    srv = server.ReplayServer()
    srv.run()