import {Component} from 'angular2/core';
import {Api} from '../common/api';

import {Team} from '../teams/service';

export class Group
{
	_id: number;
	name: string;
	seed: number;
	teams: Array<Team>;
}

@Component({})
export class GroupService
{
	api: Api;

	constructor(api: Api)
	{
		this.api = api;
	}

	get()
	{
		return this.api.get('group');
	}
	
	private getIds(teams:Array<Team>)
	{
		let teamIds: Array<string> = [];
		teams.forEach(element => {
			teamIds.push(element._id);
		});
		return teamIds;
	}
	
	add(name: string, teams: Array<Team>)
	{
		let group = {
			'name': name,
			'teams': this.getIds(teams)
		};
		return this.api.post('group', JSON.stringify(group));
	}
	
	addMany(groups: Array<Group>)
	{
		let g = [];
		groups.forEach(group => {
			let teamIds = this.getIds(group.teams); 
			g.push({
				'name': group.name,
				'teams': teamIds
			});
		});
		return this.api.post('groups', JSON.stringify({'groups': g}));
	}
}
