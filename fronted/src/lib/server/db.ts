import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as authSchema from './auth-schema';

const url = process.env.DATABASE_URL || 'postgresql://axon:axon123@127.0.0.1:5432/axon_db';
const isLocal = /localhost|127\.0\.0\.1/.test(url);

const client = postgres(url, {
	prepare: false,
	max: isLocal ? 10 : 1,
	ssl: isLocal ? false : 'require',
});

export const db = drizzle(client, { schema: authSchema });
