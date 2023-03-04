import { Mutex } from "@mangoplace/util/mutex";

export interface Waited {
	waited: boolean
}

export class Waitable<T> {
	private readonly mutex = new Mutex();
	private readonly waiterResolvers = new Set<[(value: T) => boolean, () => void]>();
	private value: T;

	constructor(initialValue: T) {
		this.value = initialValue;
	}

	public get(): T {
		return this.value;
	}

	public async set(setter: (value: T) => T): Promise<void> {
		await this.mutex.with(async () => {
			this.value = setter(this.value);

			for (const waiterAndResolver of this.waiterResolvers) {
				const [waiter, resolver] = waiterAndResolver;

				if (waiter(this.value)) {
					this.waiterResolvers.delete(waiterAndResolver);

					resolver();
				}
			}
		});
	}

	public async waitUntil(condition: (value: T) => boolean): Promise<Waited> {
		return (
			await this.mutex.with(async () => {
				if (condition(this.value)) {
					return [
						Promise.resolve({
							waited: false
						})
					];
				}

				return [
					new Promise<Waited>(resolve => {
						this.waiterResolvers.add([condition, () => resolve({waited: true})]);
					})
				];
			})
		)[0];
	}
}
