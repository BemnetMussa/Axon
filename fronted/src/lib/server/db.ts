import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as authSchema from './auth-schema';

const url = process.env.DATABASE_URL || 'postgresql://axon:axon123@127.0.0.1:5432/axon_db';

const client = postgres(url, { prepare: false, max: 10 });

export const db = drizzle(client, { schema: authSchema });
