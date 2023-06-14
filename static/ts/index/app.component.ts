import { Component, ElementRef, ViewChild } from "@angular/core";
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

	@ViewChild("password_input")
	private readonly passwordElement!: ElementRef<HTMLInputElement>;

	@ViewChild("password_confirm_input")
	private readonly passwordConfirmElement!: ElementRef<HTMLInputElement>;

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
		if (
			this.passwordElement.nativeElement.value ==
			this.passwordConfirmElement.nativeElement.value
		) {
			this.passwordConfirmElement.nativeElement.setCustomValidity("");
		} else {
			this.passwordConfirmElement.nativeElement.setCustomValidity("Passwords don't match.");
		}
	}
}
