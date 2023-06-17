import { AfterViewInit, ChangeDetectionStrategy, ChangeDetectorRef, Component, ElementRef, OnDestroy, ViewChild } from "@angular/core";
import { BoardRateLimiter } from "@mangoplace/board/ratelimiter/boardratelimiter";
import { BoardToastManager } from "@mangoplace/board/toastmanager/boardtoastmanager";
import * as bootstrap from "bootstrap";
import { Subscription } from "rxjs";

@Component({
	selector: "board-toast-container",
	templateUrl: "./boardtoastcontainer.component.html"
})
export class BoardToastContainerComponent implements AfterViewInit, OnDestroy {
	@ViewChild("rateLimitMetToast")
	private readonly rateLimitMetToast!: ElementRef<HTMLCanvasElement>;
	public secondsRemainingUntilPlacement = 0;
	private showToastSubscription!: Subscription;

	public constructor(
		public readonly boardRateLimiter: BoardRateLimiter,
		private readonly boardToastManager: BoardToastManager,
	) {}

	public ngAfterViewInit(): void {
		const rateLimitMetBootstrapToast =
			bootstrap.Toast.getOrCreateInstance(this.rateLimitMetToast.nativeElement);

		this.showToastSubscription = this.boardToastManager.showToast.subscribe(() => {
			this.secondsRemainingUntilPlacement = this.boardRateLimiter.getSecondsRemaining();

			rateLimitMetBootstrapToast.show();
		});
	}

	public ngOnDestroy(): void {
		this.showToastSubscription.unsubscribe();
	}
}
