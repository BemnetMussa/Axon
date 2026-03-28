import type { Session, User } from 'better-auth/types';


declare global {
	namespace App {
		interface Locals {
			session: Session | null;
			user: User | null;
		}
	}
}

export {};
