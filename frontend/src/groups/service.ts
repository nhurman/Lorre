import {Component} from 'angular2/core';
import {Api} from '../common/api';

import {Team} from '../teams/service';

export class Group
{
	_id;
	name: string;
	seed: number;
	teams: Array<Team>;

	constructor()
	{
		this.name = '';
		this.seed = 0;
		this.teams = [];
	}
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

	getOne(id: string)
	{
		return this.api.get('group/' + id);
	}

	private getIds(teams:Array<Team>)
	{
		let teamIds: Array<string> = [];
		teams.forEach(element => {
			teamIds.push(element._id);
		});
		return teamIds;
	}

	add(g: Group)
	{
		let group = {
			'name': name,
			'teamIds': this.getIds(g.teams)
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
				'teamIds': teamIds
			});
		});
		return this.api.post('groups', JSON.stringify({'groups': g}));
	}

	update(g: Group)
	{
		let group = {
			'name': g.name,
			'teamIds': this.getIds(g.teams)
		};
		return this.api.put('group/' + g._id, JSON.stringify(group));
	}

	delete(group: Group)
	{
		return this.api.delete('group/' + group._id);
	}
}
