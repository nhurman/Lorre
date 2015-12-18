import json
from bottle import Bottle, request, response, abort, HTTPResponse
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import cassiopeia.riotapi
from cassiopeia.type.api.exception import APIError
from cassiopeia.type.core.common import LoadPolicy

db = MongoClient('mongodb://localhost').lorre
api = Bottle()

cassiopeia.riotapi.set_load_policy(LoadPolicy.lazy);
cassiopeia.riotapi.set_region("EUW")
cassiopeia.riotapi.set_api_key("")


def send_response(code, message=None):
    r = HTTPResponse(status=code)
    r.add_header('Access-Control-Allow-Origin', '*')
    r.set_header('Content-Type', 'application/json')
    if type(message) is str:
        e = {"details": message}
        r.body = json.dumps(e)
    elif type(message) is dict:
        r.body = json.dumps(message)
    else:
        r.body = message
    return r


@api.route('/rest/player', method='POST')
def post_player():
    try:
        data = request.body.read().decode('utf-8')
        p = json.loads(data)
        summoner = cassiopeia.riotapi.get_summoner_by_name(p['name'])
        player = {'_id': summoner.id, 'name': summoner.name}
        try:
            leagues = summoner.league_entries()
            solo = [l for l in leagues if l.queue.value == 'RANKED_SOLO_5x5'][0]
            player['tier'] = solo.tier.value
            player['division'] = solo.entries[0].division.value
            player['points'] = solo.entries[0].league_points
        except (KeyError, IndexError, APIError):
            pass
        db['player'].insert_one(player)
    except (ValueError, KeyError, TypeError, APIError):
        return send_response(400)
    except DuplicateKeyError:
        return send_response(400, "Entity already exists")
    return send_response(201, player)


@api.route('/rest/player', method='GET')
def get_player():
    return {'playerList': list(db['player'].find().sort('_id', 1))}


@api.route('/rest/seed', method='GET')
def get_seed():
    def calculate_score(tier, division, points):
        tier_points = {
            'BRONZE': 0,
            'SILVER': 500,
            'GOLD': 1000,
            'PLATINUM': 1500,
            'DIAMOND': 2000,
            'MASTER': 2500,
            'CHALLENGER': 2500
        }

        division_points = {
            'V': 0,
            'IV': 100,
            'III': 200,
            'II': 300,
            'I': 400
        }

        score = tier_points[tier] + points
        if tier not in ['MASTER', 'CHALLENGER']:
            score += division_points[division]

        return score

    players = list(db['player'].find())
    for p in players:
        try:
            p['_seed'] = calculate_score(p['tier'], p['division'], p['points'])
        except KeyError:
            p['_seed'] = 0
    return send_response(200, {'playerList': players})


@api.route('/rest/match', method='GET')
def get_matches():
    team1 = {'_id': 1, 'name': 'Team1'}
    team2 = {'_id': 2, '_name': 'Team2'}
    match = [{'_id': 10, 'team1': team1, 'team2': team2, 'score1': 0, 'score2': 0, 'state': 'ongoing'}]
    return {'matchList': match}
    # m = db['match'].find()
    # return m


@api.route('/rest/team', method='PUT')
def put_team():
    data = request.body.read().decode('utf-8')
    team = json.loads(data)
    db['team'].insert_one(team)


"""
GET /matches/?filter={"ongoing":true}
[{
    _id: 123,
    team1: {_id: 123, name: 'PATRON GAMING'},
    team2: {_id: 123, name: 'JAMBONNEAUX'},
    status: "game_started"
    duration: 120,
}]

GET /matches/123
{
    _id: 123,
    team1: {_id: 123, name: 'PATRON GAMING'},
    team2: {_id: 123, name: 'JAMBONNEAUX'},
    status: "game_started"
    duration: 120,
}
"""

"""

def create_tournament():
    provider_id = api.register_provider(callback_url='http://test/callback', region='euw')
    tournament_id = api.register_tournament(provider_id)
    tournament_codes = []
    tournament_codes.add(api.request_code())
    tournament_codes.add(api.request_code())
    tournament_codes.add(api.request_code())
    tournament_codes.add(api.request_code())
"""