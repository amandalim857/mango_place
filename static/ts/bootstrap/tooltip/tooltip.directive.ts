import { AfterViewInit, Directive, ElementRef, OnDestroy } from "@angular/core";
import * as bootstrap from "bootstrap";

@Directive({
	selector: "[tooltip]"
})
export class TooltipDirective implements AfterViewInit, OnDestroy {
	private tooltip?: bootstrap.Tooltip;

	constructor (private readonly element: ElementRef) {}

	public ngAfterViewInit(): void {
		this.tooltip = new bootstrap.Tooltip(this.element.nativeElement);
	}

	public ngOnDestroy(): void {
		this.tooltip?.dispose();
	}
}
