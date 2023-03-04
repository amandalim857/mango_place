import { Component, EventEmitter, Input, Output } from "@angular/core";

@Component({
	selector: "board-control-button",
	styleUrls: ["./boardcontrolbutton.component.scss"],
	templateUrl: "./boardcontrolbutton.component.html"
})
export class BoardControlButtonComponent {
	@Input() public readonly category?: string
	@Input() public readonly checked?: boolean
	@Input() public readonly color?: string
	@Input() public readonly icon?: string
	@Input() public readonly inputId?: string
	@Input() public readonly title!: string

	@Output() public readonly click = new EventEmitter<void>();
}
