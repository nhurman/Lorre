import {Component} from 'angular2/core';

@Component({
	moduleId: module.id,
	selector: 'match-list',
	templateUrl: 'matches.html',
	styleUrls: ['matches.css']
})
export class Matches
{
	attr: string;

	constructor()
	{
		this.attr = "value";
	}
}