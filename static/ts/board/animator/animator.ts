import { Mutex } from "@mangoplace/util/mutex";
import { Waitable } from "@mangoplace/util/waitable";

interface Animation<State> {
	left: number
	current: number
	right: number
	start: Date
	end: Date
	executor: Executor<State>
}

export type Executor<State> = (state: State, currentValue: number) => State;

class LatencyTracker {
	private frameCount = 0;
	private lastRenderTime?: Date;
	private latencyAverage?: number;
	private latencyTarget: number;

	constructor(private readonly renderer: () => void, targetFramerate: number) {
		this.latencyTarget = 1000 / targetFramerate;
	}

	public get expectedLatency() {
		return this.latencyAverage ?? this.latencyTarget;
	}

	public async render(): Promise<void> {
		const now = new Date();

		if (this.lastRenderTime) {
			const lastRenderDuration = now.valueOf() - this.lastRenderTime.valueOf();

			if (this.latencyAverage) {
				this.latencyAverage =
					this.latencyAverage * this.frameCount / (this.frameCount + 1) +
						lastRenderDuration / (this.frameCount + 1);
			} else {
				this.latencyAverage = lastRenderDuration;
			}
		}

		this.frameCount++;
		this.lastRenderTime = now;

		this.renderer();
	}

	public reset(): void {
		this.lastRenderTime = undefined;
	}
}

export class Animator<AnimationType, State> {
	private readonly minimumLatency: number;
	private readonly mutexes = new Map<AnimationType, Mutex>();
	private readonly ongoing = new Map<AnimationType, Animation<State>>();
	private readonly ongoingCount = new Waitable(0);
	private renderAbortController?: AbortController;

	public state: State;

	constructor(
		initialState: State,
		private readonly renderer: (state: State) => void,
		framerateCap: number,
	) {
		this.minimumLatency = 1000 / framerateCap;

		this.state = initialState;
	}

	public destroy(): void {
		if (this.renderAbortController) {
			this.renderAbortController.abort();
		}
	}

	private estimateNextAnimationValue(
		animation: Animation<State>,
		estimatedLatency: number
	): number | undefined {
		const now = new Date();

		if (now.valueOf() >= animation.end.valueOf()) {
			return;
		}

		const remainingTime = animation.end.valueOf() - now.valueOf();
		const completedPercentage = Math.min(estimatedLatency / remainingTime, 1);

		return animation.current + completedPercentage * (animation.right - animation.current);
	}

	public async queueAnimation(
		generator: (state: State) => {
			type: AnimationType,
			left: number,
			right: number,
			duration: number,
			executor: Executor<State>,
		},
	): Promise<void> {
		const animation = generator(this.state);

		function getStartAndEnd(): [Date, Date] {
			const start = new Date();

			return [start, new Date(start.valueOf() + animation.duration)];
		}

		if (!this.mutexes.has(animation.type)) {
			this.mutexes.set(animation.type, new Mutex());
		}

		await this.mutexes.get(animation.type)!.with(async () => {
			const ongoing = this.ongoing.get(animation.type);

			if (ongoing) {
				// Have we already reached the target?
				if (
					(
						ongoing.left <= ongoing.right &&
							animation.left < ongoing.current &&
							animation.right < ongoing.current
					) || (
						ongoing.left > ongoing.right &&
							animation.left > ongoing.current &&
							animation.right > ongoing.current
					)
				) {
					this.ongoing.delete(animation.type);

					await this.ongoingCount.set(count => count - 1);
				} else {
					ongoing.left = ongoing.current;
					ongoing.right = animation.right;

					[ongoing.start, ongoing.end] = getStartAndEnd();
				}
			} else {
				const [start, end] = getStartAndEnd();

				this.ongoing.set(animation.type, {
					left: animation.left,
					current: animation.left,
					right: animation.right,
					start,
					end,
					executor: animation.executor
				});

				await this.ongoingCount.set(count => count + 1);
			}
		});
	}

	public async render(): Promise<void> {
		if (this.renderAbortController) {
			return;
		}

		this.renderAbortController = new AbortController();

		const waitUntilRenderAborted = new Promise<void>(resolve => {
			this.renderAbortController!.signal.addEventListener("abort", () => resolve())
		});

		const latencyTracker = new LatencyTracker(() => this.renderer(this.state), 60);
		let lastRender = Promise.resolve();
		let lastRenderDuration: number | undefined;

		while (!this.renderAbortController.signal.aborted) {
			await new Promise(
				resolve => setTimeout(resolve, this.minimumLatency - (lastRenderDuration ?? 0))
			);

			const waitResult = await Promise.any(
				[waitUntilRenderAborted, this.ongoingCount.waitUntil(count => count > 0)]
			);

			if (!waitResult) {
				break;
			}

			if (waitResult.waited) {
				latencyTracker.reset();
			}

			const timeBeforeRender = Date.now();

			let [_, updatedAny] = await Promise.all(
				[lastRender, this.updateAnimations(latencyTracker.expectedLatency)]
			);

			if (updatedAny) {
				lastRender = latencyTracker.render();
			} else {
				latencyTracker.reset();
			}

			lastRenderDuration = Date.now() - timeBeforeRender;
		}

		await lastRender;
	}

	private async updateAnimations(estimatedLatency: number): Promise<boolean> {
		let updatedAny = false;

		for (const [animationType, mutex] of this.mutexes.entries()) {
			await mutex.with(async () => {
				const animation = this.ongoing.get(animationType);

				if (animation) {
					updatedAny = true;

					const nextValue = this.estimateNextAnimationValue(animation, estimatedLatency);

					if (nextValue) {
						animation.current = nextValue;
					} else {
						this.ongoing.delete(animationType);

						await this.ongoingCount.set(count => count - 1);
					}

					this.state = animation.executor(this.state, nextValue ?? animation.right);
				}
			});
		}

		return updatedAny;
	}
}
