import { boolean, pgTable, text, timestamp } from 'drizzle-orm/pg-core';

export const user = pgTable('user', {
	id: text('id').primaryKey(),
	name: text('name').notNull(),
	email: text('email').notNull().unique(),
	emailVerified: boolean('emailVerified').notNull(),
	image: text('image'),
	createdAt: timestamp('createdAt', { mode: 'date' }).notNull(),
	updatedAt: timestamp('updatedAt', { mode: 'date' }).notNull(),
});

export const session = pgTable('session', {
	id: text('id').primaryKey(),
	userId: text('userId')
		.notNull()
		.references(() => user.id, { onDelete: 'cascade' }),
	token: text('token').notNull().unique(),
	expiresAt: timestamp('expiresAt', { mode: 'date' }).notNull(),
	ipAddress: text('ipAddress'),
	userAgent: text('userAgent'),
	createdAt: timestamp('createdAt', { mode: 'date' }).notNull(),
	updatedAt: timestamp('updatedAt', { mode: 'date' }).notNull(),
});

export const account = pgTable('account', {
	id: text('id').primaryKey(),
	userId: text('userId')
		.notNull()
		.references(() => user.id, { onDelete: 'cascade' }),
	accountId: text('accountId').notNull(),
	providerId: text('providerId').notNull(),
	accessToken: text('accessToken'),
	refreshToken: text('refreshToken'),
	accessTokenExpiresAt: timestamp('accessTokenExpiresAt', { mode: 'date' }),
	refreshTokenExpiresAt: timestamp('refreshTokenExpiresAt', { mode: 'date' }),
	scope: text('scope'),
	idToken: text('idToken'),
	password: text('password'),
	createdAt: timestamp('createdAt', { mode: 'date' }).notNull(),
	updatedAt: timestamp('updatedAt', { mode: 'date' }).notNull(),
});

export const verification = pgTable('verification', {
	id: text('id').primaryKey(),
	identifier: text('identifier').notNull(),
	value: text('value').notNull(),
	expiresAt: timestamp('expiresAt', { mode: 'date' }).notNull(),
	createdAt: timestamp('createdAt', { mode: 'date' }).notNull(),
	updatedAt: timestamp('updatedAt', { mode: 'date' }).notNull(),
});

// Web Push subscriptions. One row per browser/device a user has enabled
// notifications on (a user can have several). `endpoint` is globally unique — the
// push service's URL for this device — so re-enabling on the same device upserts
// rather than duplicating. Deleted with the user (cascade) or when the push service
// reports the subscription as gone (410/404) during a send (see push-sender.ts).
export const pushSubscription = pgTable('push_subscription', {
	id: text('id').primaryKey(),
	userId: text('userId')
		.notNull()
		.references(() => user.id, { onDelete: 'cascade' }),
	endpoint: text('endpoint').notNull().unique(),
	p256dh: text('p256dh').notNull(),
	auth: text('auth').notNull(),
	createdAt: timestamp('createdAt', { mode: 'date' }).notNull(),
});
