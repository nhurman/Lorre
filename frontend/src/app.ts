import {Component, provide} from 'angular2/core';
import {bootstrap} from 'angular2/platform/browser';

import {Http, HTTP_PROVIDERS} from 'angular2/http';
import {Router, RouteConfig, LocationStrategy, HashLocationStrategy, ROUTER_PROVIDERS, ROUTER_DIRECTIVES} from 'angular2/router';

import {Api} from './common/api';
import {Home} from './home/home';
import {Groups} from './groups/groups';
import {Teams} from './teams/teams';

@Component({
	selector: 'lr-app',
	directives: [ROUTER_DIRECTIVES],
	template: `<strong>Module:</strong>
		<a [routerLink]="['./Home']">Home</a> -
		<a [routerLink]="['./Teams/List']">Teams</a> -
		<a [routerLink]="['./Groups/List']">Groups</a>
		<br/><router-outlet></router-outlet>
	`
})
@RouteConfig([
	{ path: '/', component: Home, as: 'Home' },
	{ path: '/teams/...', component: Teams, as: 'Teams' },
	{ path: '/groups/...', component: Groups, as: 'Groups' }
])
class App {}

bootstrap(App, [
	HTTP_PROVIDERS,
	ROUTER_PROVIDERS,
	provide(LocationStrategy, {useClass: HashLocationStrategy}),
	Api
]);