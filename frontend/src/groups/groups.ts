import {Component} from 'angular2/core';
import {RouteConfig, ROUTER_DIRECTIVES} from 'angular2/router';
import {COMMON_DIRECTIVES} from 'angular2/common';

import {Group, GroupService} from './service';
import {Team, TeamService} from '../teams/service';

@Component({
	template: require('./list.html'),
	providers: [GroupService],
	directives: [COMMON_DIRECTIVES]
})
export class GroupsList
{
	service: GroupService;
	groups: Array<Group>;
	
	constructor(service: GroupService)
	{
		this.service = service;
		this.groups = [];
		service.get().subscribe(d => this.dataReady(d.json().results));
	}
	
	dataReady(groups: Array<Group>)
	{
		groups.forEach(element => {
			let seed = element.teams.reduce((prev, current) => prev + current.seed, 0);
			console.log(seed);
			element.seed = Math.round(seed / element.teams.length); 
		});
		
		this.groups = groups;
	}
}

@Component({
	template: require('./add.html'),
	providers: [GroupService, TeamService],
	directives: [COMMON_DIRECTIVES]
})
export class GroupsAdd
{
	teams: Array<Team>;
	groupTeams: Array<Team>;
	service: GroupService;
	teamService: TeamService;
	
	constructor(service: GroupService, teamService: TeamService)
	{
		this.service = service;
		this.teamService = teamService;
		this.teams = [];
		this.groupTeams = [];
		this.teamService.get().subscribe(d => this.teams = d.json().results.sort((a, b) => a.seed < b.seed ? 1 : -1));
	}
	
	add(name: string, teams: Array<Team>)
	{
		this.service.add(name, teams).subscribe();
	}
	
	addTeam(team: Team)
	{
		if (this.groupTeams.indexOf(team) >= 0)
			return;
		let i = this.teams.indexOf(team);
		this.groupTeams.push(team);
		this.groupTeams.sort((a, b) => a.seed < b.seed ? 1 : -1);
		this.teams.splice(i, 1);
	}
	
	removeTeam(team: Team)
	{
		if (this.groupTeams.indexOf(team) < 0)
			return;
		
		let i = this.groupTeams.indexOf(team);
		this.groupTeams.splice(i, 1);
		this.teams.push(team);
		this.teams.sort((a, b) => a.seed < b.seed ? 1 : -1);
	}
}

@Component({
	template: require('./generate.html'),
	providers: [GroupService, TeamService],
	directives: [COMMON_DIRECTIVES]
})
export class GroupsGenerate
{
	teams: Array<Team>;
	groups: Array<Group>;
	groupSize: number;
	evenGroups: boolean;
	divisors: Array<number>;
	service: GroupService;
	teamService: TeamService;
	
	constructor(service: GroupService, teamService: TeamService)
	{
		this.service = service;
		this.teamService = teamService;
		this.teams = [];
		this.groups = [];
		this.groupSize = 0;
		this.evenGroups = false;
		this.teamService.get().subscribe(d => this.dataReady(d.json().results));
	}
	
	dataReady(teams: Array<Team>)
	{
		this.teams = teams.sort((a, b) => a.seed < b.seed ? 1 : -1)
		
		let nb = teams.length;
		this.divisors = [];
		for (let i = Math.floor(Math.sqrt(nb)); i > 1; --i)
		{
			if (nb % i == 0)
			{
				this.divisors.push(i);
				let other = nb / i;
				if (other != i)
				{
					this.divisors.unshift(other);
				}
			}
		}
	}
	
	generate(groupSize: number)
	{
		if (groupSize <= 0) return;
		
		var nbGroups = Math.ceil(this.teams.length / groupSize);
		this.groupSize = Math.ceil(this.teams.length / nbGroups);
		this.evenGroups = (this.teams.length % nbGroups) == 0;
		 
		this.groups = [];
		for (let i = 0; i < nbGroups; ++i)
		{
			let g = new Group();
			g.name = 'Group ' + (i + 1);
			g.teams = [];
			g.seed = 0;
			this.groups.push(g); 
		}
		
		for (let t = 0; t < this.teams.length; ++t)
		{
			let g = t % nbGroups;
			this.groups[g].teams.push(this.teams[t]);
			this.groups[g].seed += this.teams[t].seed;
		}
		
		for (let g = 0; g < nbGroups; ++g)
		{
			this.groups[g].seed = Math.round(this.groups[g].seed / this.groups[g].teams.length);
		}
	}
	
	save()
	{
		this.service.addMany(this.groups).subscribe();
	}
}

@Component({
	directives: [ROUTER_DIRECTIVES],
	template: `
		<strong>Groups:</strong>
		<a [routerLink]="['./List']">List</a> -
		<a [routerLink]="['./Add']">Add</a> -
		<a [routerLink]="['./Generate']">Generate</a>
		<hr/>
		<router-outlet></router-outlet>`
})
@RouteConfig([
	{ path: '/', component: GroupsList, as: 'List' },
	{ path: '/add', component: GroupsAdd, as: 'Add' },
	{ path: '/generate', component: GroupsGenerate, as: 'Generate' }
])
export class Groups {}