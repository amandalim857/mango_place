import { AfterViewInit, Component, ElementRef, Input, OnDestroy, ViewChild } from "@angular/core";
import { Animator } from "@mangoplace/board/animator/animator";
import { BoardMode } from "@mangoplace/board/board";

enum AnimationType {
	FORCEFUL_RERENDER,
	PAN,
	ZOOM
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
	public selectedColor = "#a9a9a9";
	private _selectedMode = BoardMode.PAN;

	private animator!: Animator<AnimationType, Transformation>;

	private drawGrid = this.withContext(context => {
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

	private drawHoveredCell = this.withContext((context, transformation) => {
		if (this.selectedMode == BoardMode.PLACE && this.mouseOffsetX && this.mouseOffsetY) {
			const [inverseX, inverseY] =
				this.inverselyTransformed(transformation, this.mouseOffsetX, this.mouseOffsetY);

			if (
				inverseX >= 0 && inverseX < this.canvasSize &&
				inverseY >= 0 && inverseY < this.canvasSize
			) {
				context.fillStyle = this.hoveredCellColor;

				const cellX = inverseX - inverseX % this.cellSize;
				const cellY = inverseY - inverseY % this.cellSize;

				context.beginPath();
				context.rect(cellX + 0.5, cellY + 0.5, this.cellSize - 1, this.cellSize - 1);
				context.fill();
			}
		}
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
				executor: state => state
			})
		);
	}

	public handleMouseDown(): void {
		this.isMouseDown = true;
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
					executor: transformation => this.translated(
						transformation,
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
			initialTransformation => ({
				type: AnimationType.ZOOM,
				left: initialTransformation.scale,
				right: initialTransformation.scale - event.deltaY / this.canvasSize,
				duration: this.zoomAnimationDuration,
				executor: (currentTransformation, zoom) => this.zoomedAbsolutely(
					currentTransformation,
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
			x: (window.innerWidth - this.canvasSize) / 2,
			y: (window.innerHeight - this.canvasSize) / 2,
			scale: 1
		}, this.withContext((context, transformation) => {
			context.resetTransform();
			context.clearRect(0, 0, window.innerWidth, window.innerHeight);

			this.drawGrid(transformation);
			this.drawHoveredCell(transformation);
		}), this.framerateCap);

		window.addEventListener("resize", this.handleWindowResize);

		this.forceRerender();

		await this.animator.render();

		this.animator.destroy();
	}

	public ngOnDestroy(): void {
		window.removeEventListener("resize", this.handleWindowResize);
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

	private translated(
		transformation: Transformation,
		deltaX: number,
		deltaY: number
	): Transformation {
		return {
			...transformation,

			x: transformation.x + deltaX,
			y: transformation.y + deltaY
		};
	}

	private zoomedAbsolutely(
		transformation: Transformation,
		x: number,
		y: number,
		zoom: number
	): Transformation {
		zoom = Math.max(zoom, this.minimumZoom);

		const [inverseX, inverseY] = this.inverselyTransformed(transformation, x, y);

		return {
			x: transformation.x + inverseX * (transformation.scale - zoom),
			y: transformation.y + inverseY * (transformation.scale - zoom),
			scale: zoom
		};
	}

	private withContext<A>(
		fn: (context: CanvasRenderingContext2D, transformation: Transformation) => A
	): (transformation: Transformation) => A {
		return transformation => {
			this.context.save();
			this.context.setTransform(
				transformation.scale,
				0,
				0,
				transformation.scale,
				transformation.x,
				transformation.y
			);

			const result = fn(this.context, transformation);

			this.context.restore();

			return result;
		}
	}
}
