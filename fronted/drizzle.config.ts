import { defineConfig } from 'drizzle-kit';

export default defineConfig({
	schema: './src/lib/server/auth-schema.ts',
	out: './drizzle',
	dialect: 'postgresql',
	dbCredentials: {
		url: process.env.DATABASE_URL || 'postgresql://axon:axon123@127.0.0.1:5432/axon_db',
	},
});
