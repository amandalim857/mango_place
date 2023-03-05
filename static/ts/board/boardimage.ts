export interface Pixel {
	row: number
	column: number
	color: string
}

export class BoardImage {
	private image: Uint8ClampedArray;

	constructor(private readonly size: number) {
		this.image = new Uint8ClampedArray(new Array(size * size * 4).fill(255));
	}

	public async getImageBitmap(): Promise<ImageBitmap> {
		return await createImageBitmap(new ImageData(this.image, this.size));
	}

	public setPixel(pixel: Pixel): void {
		let i = (pixel.row * this.size + pixel.column) * 4;

		for (let j = 0; j < 3; j++) {
			this.image[i + j] = parseInt(pixel.color.slice(j * 2 + 1, j * 2 + 3), 16);
		}
	}
}