from bson.objectid import ObjectId
from . import mson as json
from bottle import Bottle, request, response, abort, HTTPResponse
from pymongo import MongoClient
import cassiopeia.riotapi
from cassiopeia.type.api.exception import APIError
from cassiopeia.type.core.common import LoadPolicy

db = MongoClient('mongodb://localhost').lorre
api = Bottle()

cassiopeia.riotapi.print_calls(True)
cassiopeia.riotapi.set_load_policy(LoadPolicy.lazy)
cassiopeia.riotapi.set_region("EUW")
cassiopeia.riotapi.set_api_key("")


def send_response(code, message=None):
    r = HTTPResponse(status=code)
    r.add_header('Access-Control-Allow-Origin', '*')
    r.set_header('Content-Type', 'application/json')
    if type(message) is str:
        e = {'error': message}
        r.body = json.dumps(e)
    elif type(message) is dict:
        r.body = json.dumps(message)
    else:
        r.body = message
    return r


######### PLAYERS #########
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


######### TEAMS #########
@api.route('/rest/team', method='GET')
def get_team():
    teams = list(db['team'].find())
    if 'noplayers' in request.query:
        for t in teams:
            del t['players']
    return send_response(200, {'results': teams})


@api.route('/rest/team', method='POST')
def post_team():
    try:
        data = request.body.read().decode('utf-8')
        o = json.loads(data)
    except Exception:
        return send_response(400, 'Invalid JSON')

    try:
        team = {'name': str(o['name']), 'players': [], 'seed': 0}
    except KeyError:
        return send_response(400, 'Missing parameters')

    try:
        summoners = cassiopeia.riotapi.get_summoners_by_name(o['players'])
        if any(None is a for a in summoners):
            raise FileNotFoundError
    except (FileNotFoundError, APIError):
        return send_response(400, 'Summoner not found')

    try:
        summoners_leagues = cassiopeia.riotapi.get_league_entries_by_summoner(summoners)
        leagues = {}
        for summoner_leagues in summoners_leagues:
            for league in summoner_leagues:
                if league.queue.value != 'RANKED_SOLO_5x5':
                    continue
                leagues[league.entries[0].summoner.id] = league
                break

        for summoner in summoners:
            if summoner is None:
                pass
            player = {'_id': summoner.id, 'name': summoner.name}
            try:
                solo = leagues[summoner.id]
                player['tier'] = solo.tier.value
                player['division'] = solo.entries[0].division.value
                player['points'] = solo.entries[0].league_points
                team['seed'] += calculate_score(player['tier'], player['division'], player['points'])
            except (KeyError, IndexError, APIError):
                pass

            team['players'].append(player)

        team['seed'] = round(team['seed'] / len(team['players']))
        _id = db['team'].insert_one(team).inserted_id
    except (ValueError, KeyError, TypeError, AttributeError, APIError):
        return send_response(400, 'Invalid input')
    return send_response(201, {'id': _id})


######### GROUPS #########
@api.route('/rest/group', method='GET')
def get_group():
    groups = list(db['group'].find())
    for group in groups:
        criteria = {'$or': [{'_id': i} for i in group['teams']]}
        teams = list(db['team'].find(criteria, {'players': 0}))
        # We want to keep the same order
        for i in range(len(teams)):
            id = group['teams'][i]
            team = next(filter(lambda x: x['_id'] == id, teams))
            group['teams'][i] = team
    return send_response(200, {'results': groups})


@api.route('/rest/group/<gid>', method='GET')
def get_group_one(gid):
    try:
        gid = ObjectId(gid)
    except Exception:
        return send_response(400, 'Invalid ID')
    group = db['group'].find_one({'_id': gid})
    if group is None:
        return send_response(404, 'Group not found')
    criteria = {'$or': [{'_id': i} for i in group['teams']]}
    teams = list(db['team'].find(criteria, {'players': 0}))
    # We want to keep the same order
    for i in range(len(teams)):
        id = group['teams'][i]
        team = next(filter(lambda x: x['_id'] == id, teams))
        group['teams'][i] = team
    return send_response(200, group)


def validate_group(o):
    if len(o['teamIds']) == 0:
        return send_response(400, 'The list of teams cannot be empty')
    criteria = {'$or': [{'_id': i} for i in o['teamIds']]}
    if db['team'].find(criteria).count() != len(o['teamIds']):
        return send_response(400, 'Unknown team')
    return None


@api.route('/rest/group', method='POST')
def post_group():
    try:
        data = request.body.read().decode('utf-8')
        o = json.loads(data)
    except Exception:
        return send_response(400, 'Invalid JSON')

    try:
        r = validate_group(o)
        if r is not None:
            return r

        teams = []
        for t in o['teamIds']:
            teams.append(ObjectId(t))

        group = {
            'name': str(o['name']),
            'teams': teams
        }

        _id = db['group'].insert_one(group).inserted_id
        return send_response(201, {'id': _id})
    except (TypeError, KeyError):
        return send_response(400, 'Invalid input')


@api.route('/rest/groups', method='POST')
def post_group():
    try:
        data = request.body.read().decode('utf-8')
        g = json.loads(data)
    except Exception:
        return send_response(400, 'Invalid JSON')

    try:
        # Validate everything first
        for o in g['groups']:
            r = validate_group(o)

            teams = []
            for t in o['teamIds']:
                teams.append(ObjectId(t))
            o['teams'] = teams

            if r is not None:
                return r

        # Save everything if we got this far
        ids = []
        for o in g['groups']:
            group = {
                'name': o['name'],
                'teams': o['teams']
            }
            ids.append(db['group'].insert_one(group).inserted_id)
        return send_response(201, {'ids': ids})
    except (TypeError, KeyError):
        return send_response(400, 'Invalid input')


@api.route('/rest/group/<gid>', method='OPTIONS')
def delete_group_options(gid):
    r = HTTPResponse(status=200)
    r.add_header('Access-Control-Allow-Origin', '*')
    r.add_header('Access-Control-Allow-Methods', 'GET, DELETE, PUT')
    return r


@api.route('/rest/group/<gid>', method='PUT')
def put_group(gid):
    try:
        data = request.body.read().decode('utf-8')
        o = json.loads(data)
        gid = ObjectId(gid)
    except Exception:
        return send_response(400, 'Invalid JSON')

    try:
        r = validate_group(o)
        if r is not None:
            return r

        teams = []
        for t in o['teamIds']:
            teams.append(ObjectId(t))

        group = {
            'name': str(o['name']),
            'teams': teams
        }

        r = db['group'].update_one({'_id': gid}, {'$set': group})
        if r.matched_count == 0:
            return send_response(404, 'Group not found')
        return send_response(204 - 4)
    except (TypeError, KeyError) as e:
        raise e
        return send_response(400, 'Invalid input')


@api.route('/rest/group/<gid>', method='DELETE')
def delete_group(gid):
    try:
        gid = ObjectId(gid)
    except Exception:
        return send_response(400, 'Invalid ID')

    criteria = {'_id': gid}
    r = db['group'].delete_one(criteria)
    if r.deleted_count == 0:
        return send_response(404, 'Group not found')
    return send_response(204-4)


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