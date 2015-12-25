import {Component, provide} from 'angular2/core';
import {bootstrap} from 'angular2/platform/browser';

import {Http, HTTP_PROVIDERS} from 'angular2/http';
import {Router, RouteConfig, LocationStrategy, HashLocationStrategy, ROUTER_PROVIDERS, ROUTER_DIRECTIVES} from 'angular2/router';

import {MessageComponent, MessageEmitter, LoaderComponent, LoaderEmitter} from './common/message';
import {Api} from './common/api';
import {Home} from './home/home';
import {Groups} from './groups/groups';
import {Teams} from './teams/teams';

@Component({
	selector: 'lr-app',
	directives: [ROUTER_DIRECTIVES, MessageComponent, LoaderComponent],
	template: `
		<lr-message></lr-message>
		<lr-loader></lr-loader>
		<strong>Module:</strong>
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
export class App {}

bootstrap(App, [
	HTTP_PROVIDERS,
	ROUTER_PROVIDERS,
	MessageEmitter, LoaderEmitter,
	provide(LocationStrategy, {useClass: HashLocationStrategy}),
	Api
]);