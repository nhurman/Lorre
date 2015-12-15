import json
from bottle import Bottle
from pymongo import MongoClient

db = MongoClient('mongodb://localhost').lorre
api = Bottle()


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
    data = api.request.body.read().decode('utf-8')
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