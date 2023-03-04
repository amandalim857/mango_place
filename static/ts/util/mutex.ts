export class Mutex {
    private unlock = Promise.resolve();

    public async lock(): Promise<() => void> {
        await this.unlock;

        let unlock: () => void;

        this.unlock = new Promise(resolve => {
            unlock = () => resolve();
        });

        return unlock!;
    }

    public async with<A>(fn: () => Promise<A>): Promise<A> {
        const unlock = await this.lock();

        const result = await fn();

        unlock();

        return result;
    }
}
