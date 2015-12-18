import {Component} from 'angular2/core';

@Component({
	moduleId: module.id,
	templateUrl: 'matches.html',
	styleUrls: ['matches.css']
})
export class Match
{
	attr: string;

	constructor()
	{
		this.attr = "value";
	}
}