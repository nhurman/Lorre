import {Component, EventEmitter} from 'angular2/core';
import {COMMON_DIRECTIVES} from 'angular2/common';

class MessageType
{
	className: string;
	humanName: string;
	constructor(className: string, humanName: string)
	{
		this.className = className;
		this.humanName = humanName;
	}

	static Success = new MessageType('message-success', 'Success');
	static Info = new MessageType('message-info', 'Information');
	static Warn = new MessageType('message-warn', 'Warning');
	static Error = new MessageType('message-error', 'Error');
}

class Message
{
	type: MessageType;
	text: string;

	constructor(type: MessageType, text: string)
	{
		this.type = type;
		this.text = text;
	}
}

export class MessageEmitter extends EventEmitter<Message>
{
	success(text: string)
	{
		return this.emit(new Message(MessageType.Success, text));
	}

	info(text: string)
	{
		return this.emit(new Message(MessageType.Info, text));
	}

	warn(text: string)
	{
		return this.emit(new Message(MessageType.Warn, text));
	}

	error(text: string)
	{
		return this.emit(new Message(MessageType.Error, text));
	}
}

@Component({
	directives: [COMMON_DIRECTIVES],
	selector: 'lr-message',
	template: '<div *ngIf="showMessage" [class]="msg.type.className" (click)="close()" style="background: white;position:relative;z-index:101">{{ msg.type.humanName }}: {{ msg.text }}</div>'
})
export class MessageComponent
{
	showMessage: boolean;
	msg: Message;

	constructor(emitter: MessageEmitter)
	{
		this.showMessage = false;
		emitter.subscribe(this.messageReceived.bind(this));
	}

	messageReceived(next: Message)
	{
		this.showMessage = true;
		this.msg = next;
	}

	close()
	{
		this.showMessage = false;
	}
}

const LOADER_GRACE_PERIOD = 500; // ms
export class LoaderEmitter extends EventEmitter<number>
{

	start()
	{
		setTimeout(() => this.emit(1), LOADER_GRACE_PERIOD);
	}

	stop()
	{
		return this.emit(-1);
	}
}

@Component({
	directives: [COMMON_DIRECTIVES],
	selector: 'lr-loader',
	styles: [`
		#loader {
			position: fixed;
			top: 0;
			left: 0;
			background: rgba(0, 0, 0, 0.9);
			z-index: 100;
			width: 100%;
			height: 100%;
		}
		#loader div {
			background: white;
			position: relative;
			top: 50%;
			left: 50%;
			vertical-align: middle;
			height: 100px;
			line-height: 100px;
			width: 200px;
			margin-left: -100px;
			margin-top: -50px;
			text-align: center;
		}`],
	template: '<div *ngIf="loadingCount &gt; 0" id="loader"><div>Loading ({{ loadingCount }})</div></div>'
})
export class LoaderComponent
{
	loadingCount: number;

	constructor(emitter: LoaderEmitter)
	{
		this.loadingCount = 0;
		emitter.subscribe(this.eventReceived.bind(this));
	}

	eventReceived(next: number)
	{
		this.loadingCount += next;
	}
}