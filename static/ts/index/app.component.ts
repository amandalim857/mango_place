import { Component, ElementRef, QueryList, ViewChildren } from "@angular/core";
import { AuthDetector } from "@mangoplace/util/authdetector";

enum AppModal {
	None,
	Landing,
	LogIn,
	SignUp
}

enum AppModalError {
	AccountExists,
	IncorrectPassword,
	NonexistentUsername
}

@Component({
	selector: "app",
	styleUrls: ["./app.component.scss"],
	templateUrl: "./app.component.html"
})
export class AppComponent {
	public AppModal = AppModal;
	public AppModalError = AppModalError;

	public error?: AppModalError;
	public shownModal: AppModal = AppModal.Landing;

	@ViewChildren("passwordInput")
	private readonly passwordElements!: QueryList<ElementRef<HTMLInputElement>>;

	@ViewChildren("passwordConfirmInput")
	private readonly passwordConfirmElements!: QueryList<ElementRef<HTMLInputElement>>;

	constructor(authDetector: AuthDetector) {
		if (authDetector.isAuthenticated()) {
			this.shownModal = AppModal.None;

			return;
		}

		const errorQueryParameter = new URLSearchParams(window.location.search).get("error");

		if (errorQueryParameter) {
			this.error = {
				"account_exists": AppModalError.AccountExists,
				"incorrect_password": AppModalError.IncorrectPassword,
				"nonexistent_username": AppModalError.NonexistentUsername
			}[errorQueryParameter];
		}

		if (this.error == AppModalError.AccountExists) {
			this.shownModal = AppModal.SignUp;
		} else if (
			this.error == AppModalError.IncorrectPassword ||
			this.error == AppModalError.NonexistentUsername
		) {
			this.shownModal = AppModal.LogIn;
		}
	}

	public validatePasswordConfirmation(): void {
		this.passwordElements.forEach((passwordElement, i) => {
			const passwordConfirmElement = this.passwordElements.get(i)!;

			if (
				passwordElement.nativeElement.value ==
				passwordConfirmElement.nativeElement.value
			) {
				passwordConfirmElement.nativeElement.setCustomValidity("");
			} else {
				passwordConfirmElement.nativeElement.setCustomValidity("Passwords don't match.");
			}
		});
	}
}
