import {Component} from 'angular2/core';
import {Api} from '../common/api';

export class Player
{
	_id: number;
	name: string;
	tier: string;
	division: string;
	points: number;
}

export class Team
{
	_id;
	name: string;
	seed: number;
	players: Array<Player>;

	constructor()
	{
		this.name = '';
		this.seed = 0;
		this.players = [];
	}
}

@Component({})
export class TeamService
{
	api: Api;

	constructor(api: Api)
	{
		this.api = api;
	}

	get(withPlayers: boolean = false)
	{
		let url = 'team';
		if (!withPlayers) url += '?noplayers';
		return this.api.get(url);
	}

	getOne(id: string)
	{
		return this.api.get('team/' + id);
	}

	add(name: string, players: Array<string>)
	{
		var t: any = {};
		t.name = name;
		t.players = players;

		return this.api.post('team', JSON.stringify(t));
	}

	update(id, name: string, players: Array<string>)
	{
		var t: any = {};
		t.name = name;
		t.players = players;

		return this.api.put('team/' + id, JSON.stringify(t));
	}

	delete(team: Team)
	{
		return this.api.delete('team/' + team._id);
	}

	refresh(team: Team)
	{
		return this.api.patch('team/' + team._id, '{}');
	}
}
