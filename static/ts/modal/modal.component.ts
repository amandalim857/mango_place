import { AfterViewInit, Component, ElementRef, EventEmitter, Input, Output, ViewChild } from "@angular/core";
import * as bootstrap from "bootstrap";

@Component({
	selector: "modal",
	templateUrl: "./modal.component.html"
})
export class ModalComponent implements AfterViewInit {
	private _show?: boolean;

	@Input() public readonly title: string;
	@Output() public readonly close = new EventEmitter<void>();

	@ViewChild("modal_div") private readonly modalElement: ElementRef<HTMLDivElement>;

	private modal?: bootstrap.Modal;

	@Input()
	public get show() {
		return this._show;
	}

	public set show(show: boolean) {
		this._show = show;

		if (show) {
			this.modal?.show();
		} else {
			this.modal?.hide();
		}
	}

	public ngAfterViewInit(): void {
		this.modal = new bootstrap.Modal(this.modalElement.nativeElement);

		this.modalElement.nativeElement.addEventListener("hide.bs.modal",
			(event: bootstrap.Modal.Event) => {
				if (this.show) {
					this.close.emit();

					event.preventDefault();
				}
			}
		);

		if (this.show) {
			this.modal.show();
		}
	}
}
