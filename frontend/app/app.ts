import {Component, provide} from 'angular2/core';
import {bootstrap} from 'angular2/platform/browser';

import {Http, HTTP_PROVIDERS} from 'angular2/http';
import {Router, RouteConfig, LocationStrategy, HashLocationStrategy, ROUTER_PROVIDERS, ROUTER_DIRECTIVES} from 'angular2/router';

import {Home} from './home/home';
import {Matches} from './matches/matches';

@Component({
	selector: 'lr-app',
	directives: [ROUTER_DIRECTIVES],
	template: `
		<a [routerLink]="['./Home']">Home</a> -
		<a [routerLink]="['./Matches']">Matches</a>
		<br/><router-outlet></router-outlet>
		<br/>after`
})
@RouteConfig([
	{ path: '/', component: Home, as: 'Home' },
	{ path: '/matches', component: Matches, as: 'Matches' },
])
class App {}

bootstrap(App, [
	//Http,
	HTTP_PROVIDERS,
	ROUTER_PROVIDERS,
	provide(LocationStrategy, {useClass: HashLocationStrategy})
]);