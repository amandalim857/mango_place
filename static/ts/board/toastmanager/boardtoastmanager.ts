import { EventEmitter, Injectable } from "@angular/core";

export enum BoardToast {
	RateLimitMet
}

@Injectable({
	providedIn: "root"
})
export class BoardToastManager {
	public readonly showToast = new EventEmitter<BoardToast>();
}
