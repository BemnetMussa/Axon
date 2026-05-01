import type { Session, User } from 'better-auth/types';

// global.d.ts is not picked up by SvelteKit's type system, so we put this in app.d.ts instead

declare global {
	namespace App {
		interface Locals {
			session: Session | null;
			user: User | null;
		}
	}
}

export {};
