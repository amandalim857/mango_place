import { Component, EventEmitter, Input, OnInit, Output, ViewEncapsulation } from "@angular/core";
import { BoardMode } from "@mangoplace/board/board";

@Component({
	encapsulation: ViewEncapsulation.None,
	selector: "board-controls",
	styleUrls: ["./boardcontrols.component.scss"],
	templateUrl: "./boardcontrols.component.html"
})
export class BoardControlsComponent implements OnInit {
	public readonly BoardMode = BoardMode;

	@Input() public readonly defaultColor!: string;
	@Input() public readonly defaultMode!: BoardMode;

	@Output() public readonly changeColor = new EventEmitter<string>();
	@Output() public readonly changeMode = new EventEmitter<BoardMode>();

	public readonly colorPresets = [
		{
			color: "#f94144",
			name: "red"
		},

		{
			color: "#f3722c",
			name: "dark orange"
		},

		{
			color: "#f8961e",
			name: "orange"
		},

		{
			color: "#f9c74f",
			name: "yellow"
		},

		{
			color: "#90be6d",
			name: "green"
		},

		{
			color: "#43aa8b",
			name: "green"
		},

		{
			color: "#577590",
			name: "blue"
		}
	];

	public colorPickerColor!: string;

	public ngOnInit(): void {
		const defaultColorIsPreset =
			this.colorPresets.some(preset => preset.color == this.defaultColor);

		this.colorPickerColor = defaultColorIsPreset ? "#a9a9a9" : this.defaultColor;
	}

	public handleColorPickerInput(event: Event): void {
		this.changeColor.emit(
			this.colorPickerColor = (event.currentTarget as HTMLInputElement).value
		);
	}
}
