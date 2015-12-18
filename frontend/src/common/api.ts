import {Component} from 'angular2/core';
import {Http, Response, RequestOptionsArgs, HTTP_PROVIDERS} from 'angular2/http';
import {Observable} from 'rxjs/Observable';

@Component({})
export class Api
{
	private http: Http;

	constructor(http: Http)
	{
		this.http = http;
	}
	
	getApiRoot(): string
	{
		return 'http://localhost:8081/rest/';
	}

	get(url: string, options?: RequestOptionsArgs): Observable<Response> 
	{
		url = this.getApiRoot() + url;
		return this.http.get(url, options);
	}

	post(url: string, body: string, options?: RequestOptionsArgs): Observable<Response>
	{
		url = this.getApiRoot() + url;
		return this.http.post(url, body, options);
	}
}