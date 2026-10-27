-- Web Push subscriptions. Apply with: psql "$DATABASE_URL" -f drizzle/0001_push_subscription.sql

CREATE TABLE IF NOT EXISTS "push_subscription" (
	"id" text PRIMARY KEY NOT NULL,
	"userId" text NOT NULL REFERENCES "user"("id") ON DELETE CASCADE,
	"endpoint" text NOT NULL UNIQUE,
	"p256dh" text NOT NULL,
	"auth" text NOT NULL,
	"createdAt" timestamp NOT NULL
);

CREATE INDEX IF NOT EXISTS "push_subscription_userId_idx" ON "push_subscription" ("userId");
