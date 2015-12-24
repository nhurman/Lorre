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
}

@Component({})
export class TeamService
{
	api: Api;

	constructor(api: Api)
	{
		this.api = api;
	}

	get(withPlayers: boolean = true)
	{
		let url = 'team';
		if (!withPlayers) url += '?noplayers';
		return this.api.get(url);
	}

	add(name: string, players: Array<string>)
	{
		var t: any = {};
		t.name = name;
		t.players = players;

		return this.api.post('team', JSON.stringify(t));
	}
}
