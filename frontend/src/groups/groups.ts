import {Component} from 'angular2/core';
import {RouteConfig, RouteParams, ROUTER_DIRECTIVES} from 'angular2/router';
import {COMMON_DIRECTIVES} from 'angular2/common';

import {Group, GroupService} from './service';
import {Team, TeamService} from '../teams/service';

@Component({
	template: require('./list.html'),
	providers: [GroupService],
	directives: [COMMON_DIRECTIVES, ROUTER_DIRECTIVES]
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
			element.seed = Math.round(seed / element.teams.length);
		});

		this.groups = groups;
	}

	delete(group: Group)
	{
		this.service.delete(group).subscribe(() => this.groups.splice(this.groups.indexOf(group), 1));
	}
}

@Component({
	template: require('./add.html'),
	providers: [GroupService, TeamService],
	directives: [COMMON_DIRECTIVES]
})
export class GroupsAdd
{
	group: Group;

	availableTeams: Array<Team>;
	groupService: GroupService;
	teamService: TeamService;

	constructor(service: GroupService, teamService: TeamService)
	{
		this.groupService = service;
		this.teamService = teamService;
		this.group = new Group();
		this.availableTeams = [];
		this.teamService.get(false).subscribe(d => { this.availableTeams = d.json().results.sort((a, b) => a.seed < b.seed ? 1 : -1); this.filterTeams(); });
	}

	filterTeams()
	{
		this.group.teams.forEach(team => {
			for (let i = 0; i < this.availableTeams.length; ++i)
			{
				if (this.availableTeams[i]._id == team._id)
				{
					this.availableTeams.splice(i, 1);
					break;
				}
			}
		});
	}

	save(name: string, teams: Array<Team>)
	{
		this.group.name = name;
		this.group.teams = teams;
		this.groupService.add(this.group).subscribe();
	}

	addTeam(team: Team)
	{
		if (this.group.teams.indexOf(team) >= 0)
			return;

		let i = this.availableTeams.indexOf(team);
		this.group.teams.push(team);
		this.group.teams.sort((a, b) => a.seed < b.seed ? 1 : -1);
		this.availableTeams.splice(i, 1);
	}

	removeTeam(team: Team)
	{
		if (this.group.teams.indexOf(team) < 0)
			return;

		let i = this.group.teams.indexOf(team);
		this.group.teams.splice(i, 1);
		this.availableTeams.push(team);
		this.availableTeams.sort((a, b) => a.seed < b.seed ? 1 : -1);
	}
}


@Component({
	template: require('./add.html'),
	providers: [GroupService, TeamService],
	directives: [COMMON_DIRECTIVES]
})
export class GroupsView extends GroupsAdd
{
	constructor(service: GroupService, teamService: TeamService, params: RouteParams)
	{
		super(service, teamService);
		this.groupService.getOne(params.get('id')).subscribe(d => { this.group = d.json(); this.filterTeams(); });
	}

	save(name: string, teams: Array<Team>)
	{
		this.group.name = name;
		this.group.teams = teams;
		this.groupService.update(this.group).subscribe();
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
	{ path: '/:id', component: GroupsView, as: 'View' },
	{ path: '/add', component: GroupsAdd, as: 'Add' },
	{ path: '/generate', component: GroupsGenerate, as: 'Generate' }
])
export class Groups {}