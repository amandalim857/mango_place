import { AfterViewInit, Component, ElementRef, Input, OnDestroy, ViewChild } from "@angular/core";
import { Animator } from "@mangoplace/board/animator/animator";
import { BoardImage } from "@mangoplace/board/boardimage";
import { BoardMode } from "@mangoplace/board/boardmode";

enum AnimationType {
	FORCEFUL_RERENDER,
	PAN,
	PLACE,
	ZOOM
}

interface BoardState {
	image: BoardImage
	transformation: Transformation
}

interface Transformation {
	x: number
	y: number
	scale: number
}

@Component({
	selector: "board",
	styleUrls: ["./board.component.scss"],
	templateUrl: "./board.component.html"
})
export class BoardComponent implements AfterViewInit, OnDestroy {
	public readonly BoardMode = BoardMode;

	@Input() private readonly cellBorderColor!: string;
	@Input() private readonly boardSize!: number;
	@Input() private readonly framerateCap!: number;
	@Input() private readonly hoveredCellColor!: string;
	@Input() private readonly minimumZoom!: number;
	@Input() private readonly zoomAnimationDuration!: number

	@ViewChild("canvas") private readonly canvas!: ElementRef<HTMLCanvasElement>;

	private canvasSize!: number;
	private context!: CanvasRenderingContext2D;
	private isMouseDown: boolean = false;
	private mouseOffsetX?: number;
	private mouseOffsetY?: number;
	public selectedColor = "#f94144";
	private _selectedMode = BoardMode.PAN;

	private animator!: Animator<AnimationType, BoardState>;

	private drawGrid = this.withContext(async context => {
		context.lineCap = "square";
		context.strokeStyle = this.cellBorderColor;

		for (let row = 0; row < this.canvasSize + this.cellSize; row += this.cellSize) {
			context.beginPath();
			context.moveTo(0, row);
			context.lineTo(this.canvasSize, row);
			context.stroke();
		}

		for (let column = 0; column < this.canvasSize + this.cellSize; column += this.cellSize) {
			context.beginPath();
			context.moveTo(column, 0);
			context.lineTo(column, this.canvasSize);
			context.stroke();
		}
	});

	private drawHoveredCell = this.withContext(async (context, state) => {
		if (this.selectedMode == BoardMode.PLACE) {
			this.withCoordinates((_, row, column) => {
				context.fillStyle = this.hoveredCellColor;

				context.beginPath();
				context.rect(
					column * this.cellSize + 0.5,
					row * this.cellSize + 0.5,
					this.cellSize - 1,
					this.cellSize - 1
				);

				context.fill();
			})(state.transformation);
		}
	});

	private drawImage = this.withContext(async (context, state) => {
		context.imageSmoothingEnabled = false;

		context.drawImage(
			await state.image.getImageBitmap(),
			0,
			0,
			this.canvasSize,
			this.canvasSize
		);
	});

	public get cellSize(): number {
		return this.canvasSize / this.boardSize;
	}

	private async forceRerender(): Promise<void> {
		await this.animator.queueAnimation(
			() => ({
				type: AnimationType.FORCEFUL_RERENDER,
				left: 0,
				right: 0,
				duration: 0,
				executor: () => {}
			})
		);
	}

	public async handleMouseDown(): Promise<void> {
		this.isMouseDown = true;

		if (this.selectedMode == BoardMode.PLACE) {
			await this.animator.queueAnimation(
				() => ({
					type: AnimationType.PLACE,
					left: 0,
					right: 0,
					duration: 0,
					executor: state => this.placePixel(state)
				})
			);
		}
	}

	public async handleMouseMove(event: MouseEvent): Promise<void> {
		this.mouseOffsetX = event.offsetX;
		this.mouseOffsetY = event.offsetY;

		if (this.selectedMode == BoardMode.PAN && this.isMouseDown) {
			await this.animator.queueAnimation(
				() => ({
					type: AnimationType.PAN,
					left: 0,
					right: 0,
					duration: 0,
					executor: state => this.translate(
						state.transformation,
						event.movementX,
						event.movementY
					)
				})
			);
		} else if (this.selectedMode == BoardMode.PLACE) {
			await this.forceRerender();
		}
	}

	public handleMouseUpOrOut(): void {
		this.isMouseDown = false;
	}

	public async handleWheel(event: WheelEvent): Promise<void> {
		await this.animator.queueAnimation(
			state => ({
				type: AnimationType.ZOOM,
				left: state.transformation.scale,
				right: state.transformation.scale - event.deltaY / this.canvasSize,
				duration: this.zoomAnimationDuration,
				executor: (state, zoom) => this.zoomAbsolutely(
					state.transformation,
					this.mouseOffsetX ?? this.canvasSize / 2,
					this.mouseOffsetY ?? this.canvasSize / 2,
					zoom
				)
			}),
		);
	}

	public handleWindowResize = async () => {
		this.resizeCanvas();

		await this.forceRerender();
	};

	private inverselyTransformed(
		transformation: Transformation,
		x: number,
		y: number
	): [number, number] {
		return [
			(x - transformation.x) / transformation.scale,
			(y - transformation.y) / transformation.scale
		];
	}

	public async ngAfterViewInit(): Promise<void> {
		this.setCursor();

		this.context = this.canvas.nativeElement.getContext("2d")!;

		this.resizeCanvas();

		this.animator = new Animator({
			image: new BoardImage(this.boardSize),
			transformation: {
				x: (window.innerWidth - this.canvasSize) / 2,
				y: (window.innerHeight - this.canvasSize) / 2,
				scale: 1
			}
		}, this.withContext(async (context, state) => {
			context.resetTransform();
			context.clearRect(0, 0, window.innerWidth, window.innerHeight);

			await this.drawImage(state);
			await this.drawGrid(state);
			await this.drawHoveredCell(state);
		}), this.framerateCap);

		window.addEventListener("resize", this.handleWindowResize);

		this.forceRerender();

		await this.animator.render();

		this.animator.destroy();
	}

	public ngOnDestroy(): void {
		window.removeEventListener("resize", this.handleWindowResize);
	}

	private placePixel(state: BoardState): void {
		this.withCoordinates((_, row, column) => {
			state.image.setPixel({
				row,
				column,
				color: this.selectedColor
			});
		})(state.transformation);
	}

	private resizeCanvas(): void {
		this.canvasSize = Math.min(window.innerWidth, window.innerHeight);

		this.canvas.nativeElement.width = window.innerWidth;
		this.canvas.nativeElement.height = window.innerHeight;
	}

	public get selectedMode(): BoardMode {
		return this._selectedMode;
	}

	public set selectedMode(mode: BoardMode) {
		this._selectedMode = mode;

		this.setCursor();
	}

	private setCursor(): void {
		this.canvas.nativeElement.style.cursor = this.selectedMode == BoardMode.PAN ? "move" : "";
	}

	private translate(
		transformation: Transformation,
		deltaX: number,
		deltaY: number
	): void {
		transformation.x += deltaX;
		transformation.y += deltaY;
	}

	private zoomAbsolutely(
		transformation: Transformation,
		x: number,
		y: number,
		zoom: number
	): void {
		zoom = Math.max(zoom, this.minimumZoom);

		const [inverseX, inverseY] = this.inverselyTransformed(transformation, x, y);

		transformation.x += inverseX * (transformation.scale - zoom);
		transformation.y += inverseY * (transformation.scale - zoom);
		transformation.scale = zoom;
	}

	private withContext<A>(
		fn: (context: CanvasRenderingContext2D, state: BoardState) => Promise<A>
	): (state: BoardState) => Promise<A> {
		return async state => {
			this.context.save();
			this.context.setTransform(
				state.transformation.scale,
				0,
				0,
				state.transformation.scale,
				state.transformation.x,
				state.transformation.y
			);

			this.context.imageSmoothingEnabled = false;

			const result = await fn(this.context, state);

			this.context.restore();

			return result;
		};
	}

	private withCoordinates<A>(
		fn: (transformation: Transformation, row: number, column: number) => A
	): (transformation: Transformation) => A | undefined {
		return transformation => {
			if (this.mouseOffsetX && this.mouseOffsetY) {
				const [inverseX, inverseY] = this.inverselyTransformed(
					transformation,
					this.mouseOffsetX,
					this.mouseOffsetY
				);

				if (
					inverseX >= 0 && inverseX < this.canvasSize &&
					inverseY >= 0 && inverseY < this.canvasSize
				) {
					const row = Math.floor(inverseY / this.cellSize);
					const column = Math.floor(inverseX / this.cellSize);

					return fn(transformation, row, column);
				}
			}
		};
	}
}
