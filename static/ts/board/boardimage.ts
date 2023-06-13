export interface Pixel {
	row: number
	column: number
	color: string
}

export class BoardImage {
	private image: Uint8ClampedArray;

	constructor(
		private readonly size: number,
		initialRenderUrl: string,
		initialRenderCallback: () => void
	) {
		this.image = new Uint8ClampedArray(new Array(size * size * 4).fill(255));

		const imageCanvas = document.createElement("canvas");

		imageCanvas.width = size;
		imageCanvas.height = size;

		const context = imageCanvas.getContext("2d");

		if (context != null) {
			const imageElement = new Image();

			imageElement.addEventListener("load", () => {
				context.drawImage(imageElement, 0, 0);

				this.image = context.getImageData(0, 0, size, size).data;

				initialRenderCallback();
			});

			imageElement.src = initialRenderUrl;
		}
	}

	public async getImageBitmap(): Promise<ImageBitmap> {
		return await createImageBitmap(new ImageData(this.image, this.size));
	}

	public getPixelColor(row: number, column: number): string {
		const i = (row * this.size + column) * 4;

		const redComponent = this.image[i].toString(16).padStart(2, "0");
		const greenComponent = this.image[i + 1].toString(16).padStart(2, "0");
		const blueComponent = this.image[i + 2].toString(16).padStart(2, "0");

		return `#${redComponent}${greenComponent}${blueComponent}`;
	}

	public setPixel(pixel: Pixel): void {
		const i = (pixel.row * this.size + pixel.column) * 4;

		for (let j = 0; j < 3; j++) {
			this.image[i + j] = parseInt(pixel.color.slice(j * 2 + 1, j * 2 + 3), 16);
		}
	}
}
