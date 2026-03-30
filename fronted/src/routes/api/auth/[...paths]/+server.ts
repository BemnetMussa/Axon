import { auth } from '$lib/auth';
import type { RequestHandler } from './$types';

const handler: RequestHandler = async ({ request }) => {
	return auth.handler(request);
};

export const GET = handler;
export const POST = handler;
