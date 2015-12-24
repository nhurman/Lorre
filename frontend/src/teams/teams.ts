import {Component} from 'angular2/core';
import {RouteConfig, ROUTER_DIRECTIVES} from 'angular2/router';
import {COMMON_DIRECTIVES} from 'angular2/common';

import {Team, TeamService} from './service';

@Component({
	template: require('./list.html'),
	providers: [TeamService],
	directives: [COMMON_DIRECTIVES]
})
class TeamsList
{
	teams: Array<Team>;
	
	constructor(service: TeamService)
	{
		this.teams = [];
		service.get().subscribe(d => this.teams = d.json().results.sort((a, b) => a.seed < b.seed ? 1 : -1));
	}
}

@Component({
	template: require('./add.html'),
	providers: [TeamService],
	directives: [COMMON_DIRECTIVES]
})
class TeamsAdd
{	
	service: TeamService;
	constructor(service: TeamService)
	{
		this.service = service;
	}
	
	add(name: string, players: string)
	{
		var p: Array<string> = players.split('\n');
		var p2: Array<string> = [];
		for (var i = 0; i < p.length; ++i)
		{
			var s = p[i].trim();
			if (s.length > 0)
				p2.push(s);
		}
		this.service.add(name, p2).subscribe();
	}
}


@Component({
	directives: [ROUTER_DIRECTIVES],
	template: `
		<strong>Teams:</strong>
		<a [routerLink]="['./List']">List</a> -
		<a [routerLink]="['./Add']">Add</a>
		<hr/>
		<router-outlet></router-outlet>
	`
})
@RouteConfig([
	{ path: '/', component: TeamsList, as: 'List'},
	{ path: '/add', component: TeamsAdd, as: 'Add'}
])
export class Teams {}