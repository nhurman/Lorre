import {Component} from 'angular2/core';
import {RouteConfig, RouteParams, ROUTER_DIRECTIVES} from 'angular2/router';
import {COMMON_DIRECTIVES} from 'angular2/common';

import {MessageEmitter} from '../common/message';
import {Player, Team, TeamService} from './service';

@Component({
	template: require('./list.html'),
	providers: [TeamService],
	directives: [COMMON_DIRECTIVES, ROUTER_DIRECTIVES]
})
class TeamsList
{
	teams: Array<Team>;
	service: TeamService;
	msg: MessageEmitter;

	constructor(service: TeamService, msg: MessageEmitter)
	{
		this.service = service;
		this.msg = msg;
		this.teams = [];
		service.get(true).subscribe(d => this.teams = d.json().results.sort((a, b) => a.seed < b.seed ? 1 : -1));
	}

	delete(team: Team)
	{
		this.service.delete(team).subscribe(() => {
			this.teams.splice(this.teams.indexOf(team), 1);
			this.msg.success('Team ' + team.name + ' deleted');
		});
	}

	refresh(team: Team)
	{
		this.service.refresh(team).subscribe(n => {
			this.teams[this.teams.indexOf(team)] = n.json();
			this.teams.sort((a, b) => a.seed < b.seed ? 1 : -1);
			this.msg.success('Team ' + team.name + ' refreshed')
		});
	}

	refreshAll(teams: Array<Team>)
	{
		teams.forEach(element => {
			this.refresh(element);
		});
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
	team: Team;
	msg: MessageEmitter;

	constructor(service: TeamService, msg: MessageEmitter)
	{
		this.service = service;
		this.msg = msg;
		this.team = new Team();
	}

	textToPlayers(players: string)
	{
		var p: Array<string> = players.split('\n');
		var p2: Array<string> = [];
		for (var i = 0; i < p.length; ++i)
		{
			var s = p[i].trim();
			if (s.length > 0)
				p2.push(s);
		}
		return p2;
	}

	save(name: string, players: string)
	{
		let p2 = this.textToPlayers(players);
		this.service.add(name, p2).subscribe(
			n => this.msg.success('Team ' + name + ' added'),
			e => this.msg.error(e.json().error));
	}

	playersToText(players: Array<Player>)
	{
		let t: Array<string> = [];
		players.forEach(element => {
			t.push(element.name);
		});
		return t.join('\n');
	}
}

@Component({
	template: require('./add.html'),
	providers: [TeamService],
	directives: [COMMON_DIRECTIVES]
})
export class TeamsView extends TeamsAdd
{
	constructor(service: TeamService, msg: MessageEmitter, params: RouteParams)
	{
		super(service, msg);
		service.getOne(params.get('id')).subscribe(d => this.team = d.json());
	}

	save(name: string, players: string)
	{
		let p2 = this.textToPlayers(players);
		this.service.update(this.team._id, name, p2).subscribe(
			n => this.msg.success('Team ' + name + ' saved'),
			e => this.msg.error(e.json().error));
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
	{ path: '/:id', component: TeamsView, as: 'View'},
	{ path: '/add', component: TeamsAdd, as: 'Add'},
])
export class Teams {}