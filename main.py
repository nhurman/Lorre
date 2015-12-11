import cassiopeia.riotapi
from cassiopeia.type.core.common import LoadPolicy
from lorre import recorder
from lorre import server
import time

if __name__ == '_d_main__':
    cassiopeia.riotapi.set_load_policy(LoadPolicy.lazy);
    cassiopeia.riotapi.set_region("EUW")
    cassiopeia.riotapi.set_api_key("")

    while True:
        if True:
            summoner_name = 'I Haxa I'
            summoner = cassiopeia.riotapi.get_summoner_by_name(summoner_name)
            try:
                game = summoner.current_game()
            except cassiopeia.type.api.exception.APIError:
                continue
        else:
            featured = cassiopeia.riotapi.get_featured_games()
            game = featured[0]

        if game is None:
            print("Game not found, waiting 30s")
            time.sleep(30)
        else:
            rec = recorder.GameRecorder(game, recorder.Region.EUW)
            rec.download()

else:
    srv = server.ReplayServer()
    srv.run()