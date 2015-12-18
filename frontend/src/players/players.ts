import {Component} from 'angular2/core';
import {Player, PlayerService} from './service';
import {COMMON_DIRECTIVES} from 'angular2/common';

@Component({
	moduleId: module.id,
	template: require('./list.html'),
	directives: [COMMON_DIRECTIVES],
	providers: [PlayerService]
})
export class PlayersList
{
	players: Array<Player>;

	constructor(service: PlayerService)
	{
		var p1: Player = new Player();
		p1.name = "Name 1";
		
		var p2: Player = new Player();
		p2.name = "Name 2";
		
		this.players = [p1, p2];
		
		service.get().subscribe(d => this.players = d.json().playerList);
	}
}

@Component({
	moduleId: module.id,
	template: require('./add.html'),
	directives: [COMMON_DIRECTIVES],
	providers: [PlayerService]
})
export class PlayersAdd
{
	service: PlayerService;
	constructor(service: PlayerService)
	{
		this.service = service;
	}
	
	add(name: string)
	{
		this.service.add(name).subscribe();
	}
}