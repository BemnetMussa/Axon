import type { Article, Pulse } from '$lib/api';

/**
 * Content for the app screens shown on the landing page (rendered by /preview).
 * The Polars story is real (feed, Oct 6 2026) and its brief is the hosted brief
 * prompt's output for that article; the feed stories,
 * the chat answer and the digest summary are illustrative.
 */

export type PreviewScreen = 'feed' | 'read' | 'ask' | 'digest';

export const story: Article = {
	id: 6170,
	source: 'HackerNews',
	category: 'AI',
	likes: 349,
	views: 0,
	engagement_score: 0,
	url: 'https://pola.rs/posts/release-polars-2/',
	published_date: '2026-10-06T11:59:01Z',
	content_snippet: '',
	title: 'Release of Polars 2.0',
	insight: `Polars 2.0 introduces first-class SQL support, out-of-core (spill-to-disk) capabilities, and significant performance improvements. The release treats SQL as a primary interface, leveraging engine optimizations like join reordering, improved common-subplan-elimination, and dynamic predicates. On TPC-H and TPC-DS 1 benchmarks, Polars SQL reportedly outperforms DuckDB 1.5.6, DuckDB 2.0 alpha, and DataFusion 54.0.0. The team notes that while default Polars is fastest on most benchmarks, it exhibits constant overhead at 192 threads that hurts small data queries, an issue they have diagnosed and plan to fix in the next release.

The streaming engine is now the default for \`collect\` on LazyFrames, which reduces memory usage but does not guarantee row-order for operations like joins and group-bys unless \`maintain_order=True\` is set. Out-of-core processing is enabled by default, starting to spill to disk at approximately 80% of RAM with a default disk budget of 64GB. Currently, this applies to sorts, window functions, and many expressions; support for joins and group-bys is on the roadmap.

A new Map dtype is supported, mapping directly to the Arrow MapType rather than the previous \`List(Struct)\` representation. This allows for dictionary-like methods such as \`get\`, \`contains_key\`, \`len\`, \`keys\`, and \`values\`. The release also implements stricter dtype handling and explicitness, which the team states leads to faster feedback and AI iteration. Benchmark code and data generation scripts are available in a public GitHub repository for replication.`
};

export const suggestions = ['What changed from 1.x?', 'Will my LazyFrame code use less memory?', 'Should I move off pandas?'];

export const chat = [
	{ role: 'user' as const, content: 'Will my existing LazyFrame code use less memory?' },
	{
		role: 'ai' as const,
		content:
			'Yes, without changes. In 2.0, `collect` on a LazyFrame runs on the **streaming engine by default**, so data moves through in chunks instead of loading all at once.\n\nIt also **spills to disk at about 80% memory use**, so jobs that used to crash on large files should now finish. The trade-off the article mentions: some operations no longer guarantee row order, so sort explicitly if you depend on it.'
	}
];

export const digest = {
	created_at: '2026-10-14T09:00:00Z',
	content: `## The week
Google Research and NVIDIA both published work on agents doing measured tasks, and Hugging Face released a weather model that runs extreme-weather simulation at a fraction of the usual cost.

## What landed
* **Putting Earth AI to work** (Google Research): geospatial agents aimed at large-scale planet problems.
* **Analyzing technical documents with Deep Review** (Google Research): an agent that reads technical documents.
* **HiRO-ACEv2** (Hugging Face): extreme-weather simulation at 3 km resolution for a fraction of the cost.
* **NeMo Gym for chip design** (NVIDIA): measured agent reliability and tool-calling efficiency on chip-design tasks.`
};

type PoolItem = Pick<Article, 'source' | 'category' | 'likes' | 'title' | 'insight'>;

const POOL: PoolItem[] = [
	{
		source: 'ArXiv',
		category: 'Signal',
		likes: 0,
		title: 'Tool-use accuracy falls off a cliff past 40 tools',
		insight: 'A new benchmark hands agents anywhere from 5 to 200 tools and measures how often they pick the right one. Accuracy holds close to baseline until roughly 40 tools, then drops fast. Clear tool descriptions matter more than model size below that line.'
	},
	{
		source: 'GitHub',
		category: 'Momentum',
		likes: 2140,
		title: 'voice-agent-lite: sub-second voice replies on a laptop CPU',
		insight: 'A small open-source stack that streams speech-to-text, a quantized model and text-to-speech in one loop. It answers in under a second on a recent laptop with no GPU, and the repo picked up two thousand stars in six days.'
	},
	{
		source: 'Anthropic',
		category: 'AI',
		likes: 0,
		title: 'How the new model keeps track of hours-long tasks',
		insight: 'The write-up explains how the model keeps working notes, checks its own progress, and recovers when a step fails. The useful part for builders is the section on structuring long agent runs so they stay on course.'
	},
	{
		source: 'HackerNews',
		category: 'Concerns',
		likes: 412,
		title: 'Ask HN: What are you actually running on small reasoning models?',
		insight: 'A long thread of people sharing what they moved from large hosted models to small local ones. The pattern: classification, extraction and routing moved first; open-ended writing mostly stayed on large models.'
	},
	{
		source: 'HuggingFace',
		category: 'AI',
		likes: 0,
		title: 'An open 8B model that holds its own on coding evals',
		insight: 'The release notes show a small open model scoring close to much larger ones on common coding benchmarks. The weights are permissively licensed, which makes it a real option for local code assistants.'
	},
	{
		source: 'SimonW',
		category: 'Momentum',
		likes: 0,
		title: 'Prompt injection in browser agents, with working examples',
		insight: 'A clear walkthrough of how pages can hijack an agent that reads them, with reproducible examples. Worth reading before you give any agent a browser and a logged-in session.'
	},
	{
		source: 'NVIDIA',
		category: 'AI',
		likes: 0,
		title: 'New low-precision kernels cut inference cost on current GPUs',
		insight: 'The post details new kernels that run models at lower precision with little quality loss. For teams serving their own models, it is a direct cut in cost per token without changing hardware.'
	},
	{
		source: 'GoogleResearch',
		category: 'Signal',
		likes: 0,
		title: 'Small retrievers beat large ones when the index is fresh',
		insight: 'The paper finds that keeping a retrieval index up to date matters more than the size of the retrieval model. A small retriever over a fresh index beat a large one over a stale index on most tasks.'
	}
];

/** Intake-stage bubble key → feed source name. */
export const KEY_SOURCE: Record<string, string> = {
	arxiv: 'ArXiv',
	github: 'GitHub',
	anthropic: 'Anthropic',
	hn: 'HackerNews',
	huggingface: 'HuggingFace',
	nvidia: 'NVIDIA',
	google: 'GoogleResearch',
	simonw: 'SimonW'
};

let nextId = 1;

export function makeStory(i: number, minutesAgo: number, key?: string): Article {
	const match = key ? POOL.find((a) => a.source === KEY_SOURCE[key]) : undefined;
	const base = match ?? POOL[i % POOL.length];
	return {
		...base,
		id: nextId++,
		url: '#',
		views: 0,
		engagement_score: 0,
		content_snippet: base.insight ?? '',
		published_date: new Date(Date.now() - minutesAgo * 60_000).toISOString()
	};
}

/** Messages between the landing page and the /preview frames. */
export type PreviewMessage =
	| { type: 'axon-preview:keep'; key: string }
	| { type: 'axon-preview:theme'; theme: 'dark' | 'light' }
	| { type: 'axon-preview:ready' }
	| { type: 'axon-preview:keepable'; keys: string[] }
	| { type: 'axon-preview:pulse'; pulse: Pulse | null };
