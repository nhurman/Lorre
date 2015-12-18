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

@Component({})
export class PlayerService
{
	api: Api;

	constructor(api: Api)
	{
		this.api = api;
	}

	get()
	{
		return this.api.get('player');
	}
	
	add(name: string)
	{
		var p: Player = new Player();
		p.name = name;
		
		return this.api.post('player', JSON.stringify(p));
	}
}
