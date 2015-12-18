import {Component, provide} from 'angular2/core';
import {bootstrap} from 'angular2/platform/browser';

import {Http, HTTP_PROVIDERS} from 'angular2/http';
import {Router, RouteConfig, LocationStrategy, HashLocationStrategy, ROUTER_PROVIDERS, ROUTER_DIRECTIVES} from 'angular2/router';

import {Api} from './common/api';
import {Home} from './home/home';
import {PlayersList, PlayersAdd} from './players/players';

@Component({
	selector: 'lr-app',
	directives: [ROUTER_DIRECTIVES],
	template: `
		<a [routerLink]="['./Home']">Home</a> -
		<a [routerLink]="['./Players']">Players</a> -
		<a [routerLink]="['./AddPlayer']">Add</a>
		<br/><router-outlet></router-outlet>
		<br/>after`
})
@RouteConfig([
	{ path: '/', component: Home, as: 'Home' },
	{ path: '/players', component: PlayersList, as: 'Players' },
	{ path: '/players/new', component: PlayersAdd, as: 'AddPlayer' },
])
class App {}

bootstrap(App, [
	HTTP_PROVIDERS,
	ROUTER_PROVIDERS,
	provide(LocationStrategy, {useClass: HashLocationStrategy}),
	Api
]);