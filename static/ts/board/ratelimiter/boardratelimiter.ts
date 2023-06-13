import { Injectable } from "@angular/core";
import { Pixel } from "@mangoplace/board/boardimage";

@Injectable({
	providedIn: "root"
})
export class BoardRateLimiter {
	private static readonly cooldownMilliseconds = 300000;
	private lastPlacement?: Date;

	public getSecondsRemaining(): number {
		if (this.lastPlacement) {
			const millisecondsSinceLastPlacement = Date.now() - this.lastPlacement.getTime();

			return Math.floor(
				Math.max(
					BoardRateLimiter.cooldownMilliseconds - millisecondsSinceLastPlacement,
					0
				) / 1000
			);
		}

		return 0;
	}

	public async withPixelPlacement(
		placePixel: () => Promise<Pixel>,
		revertPlacement: () => Promise<void>,
	): Promise<boolean> {
		const now = new Date();

		if (!this.lastPlacement || now.getTime() - this.lastPlacement.getTime() >= BoardRateLimiter.cooldownMilliseconds) {
			this.lastPlacement = now;

			const pixel = await placePixel();
			const response = await fetch(
				`/canvas/${pixel.row}/${pixel.column}?hexcolor=${encodeURIComponent(pixel.color)}`,
				{
					method: "PUT"
				}
			);

			if (response.status == 200) {
				return true;
			}

			const waitSeconds = response.headers.get("Retry-After");

			if (waitSeconds) {
				this.lastPlacement = new Date(
					Date.now() -
					BoardRateLimiter.cooldownMilliseconds +
					parseInt(waitSeconds) * 1000
				);
			}

			await revertPlacement();
		}

		return false;
	}
}
