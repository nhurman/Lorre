import {Component} from 'angular2/core';
import {Http, Response, RequestOptionsArgs, HTTP_PROVIDERS} from 'angular2/http';
import {Observable} from 'rxjs/Observable';

import {_finally} from 'rxjs/operator/finally';
Observable.prototype.finally = _finally; // Is there a better way to do this?

import {LoaderEmitter} from './message.ts';

@Component({})
export class Api
{
	private http: Http;
	private loader: LoaderEmitter;

	constructor(http: Http, loader: LoaderEmitter)
	{
		this.http = http;
		this.loader = loader;
	}

	private getApiRoot(): string
	{
		return 'http://localhost:8081/rest/';
	}

	private chainLoader(obs: Observable<Response>)
	{
		this.loader.start();
		return obs.finally(() => this.loader.stop());
	}

	get(url: string, options?: RequestOptionsArgs): Observable<Response>
	{
		url = this.getApiRoot() + url;
		return this.chainLoader(this.http.get(url, options));
	}

	post(url: string, body: string, options?: RequestOptionsArgs): Observable<Response>
	{
		url = this.getApiRoot() + url;
		return this.chainLoader(this.http.post(url, body, options));
	}

	put(url: string, body: string, options?: RequestOptionsArgs): Observable<Response>
	{
		url = this.getApiRoot() + url;
		return this.chainLoader(this.http.put(url, body, options));
	}

	patch(url: string, body: string, options?: RequestOptionsArgs): Observable<Response>
	{
		url = this.getApiRoot() + url;
		return this.chainLoader(this.http.patch(url, body, options));
	}

	delete(url: string, options?: RequestOptionsArgs): Observable<Response>
	{
		url = this.getApiRoot() + url;
		return this.chainLoader(this.http.delete(url, options));
	}
}