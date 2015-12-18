import {Component} from 'angular2/core';
import {Http} from 'angular2/http';

export class Team
{
	_id: number;
	name: string;
}

export class Match
{
	_id: number;
	team1: Team;
	team2: Team;
	score1: number;
	score2: number;
	duration: number;
}

@Component({})
export class TournamentService
{
	http: Http;

	constructor(http: Http)
	{
		this.http = http;
	}

	GetMatches()
	{
		return this.http.get('/rest/match');
	}
}
