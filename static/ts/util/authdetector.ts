import { Injectable } from "@angular/core";

@Injectable({
	providedIn: "root"
})
export class AuthDetector {
	public isAuthenticated(): boolean {
		return (document.querySelector("meta[data-authenticated]") as HTMLElement | null)
			?.dataset
			?.authenticated == "true"
	}
}
