import { Component, ElementRef, ViewChild } from "@angular/core";

enum AppModal {
	None,
	Landing,
	LogIn,
	SignUp
}

@Component({
	selector: "app",
	styleUrls: ["./app.component.scss"],
	templateUrl: "./app.component.html"
})
export class AppComponent {
	public AppModal = AppModal;

	public shownModal: AppModal = AppModal.Landing;

	@ViewChild("password_input")
	private readonly passwordElement!: ElementRef<HTMLInputElement>;

	@ViewChild("password_confirm_input")
	private readonly passwordConfirmElement!: ElementRef<HTMLInputElement>;

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
