import type { Article, Pulse } from '$lib/api';

/**
 * Content for the app screens shown on the landing page (rendered by /preview).
 * The Polars story and its brief are real (feed, Oct 6 2026); the feed stories,
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
	insight: `Polars 2.0 marks a pivotal shift in the data engineering landscape, signaling the end of the era where speed and usability were mutually exclusive. By elevating SQL to a first-class citizen and fundamentally restructuring its execution engine, Polars has moved from being a niche performance tool to a serious contender for general-purpose data processing.

The technical substance of this release lies in its aggressive optimization of the query engine, specifically through the introduction of a default streaming engine and out-of-core capabilities. Previously, Polars was celebrated for its in-memory speed, but it often faltered when datasets exceeded available RAM. Now, calling \`collect\` on a LazyFrame defaults to the streaming engine, which drastically reduces memory footprint while maintaining high throughput.

Concurrently, the system now spills data to disk by default when memory usage hits approximately 80%, allowing queries to complete even when the dataset is larger than the machine's RAM.`
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
	content: `## The Big Picture
Agents moved from demos into tooling this week. Google Research and NVIDIA both shipped work on making agents reliable at real tasks, and the open weather-model release shows how far cheap simulation has come.

## Core Breakthroughs
- **Putting Earth AI to work: Geospatial agents for our planet's biggest challenges** (GoogleResearch)
- **Analyzing technical documents with Deep Review** (GoogleResearch)
- **HiRO-ACEv2: Simulating extreme weather at 3 km resolution for a fraction of the cost** (HuggingFace)
- **Optimizing Agent Reliability and Tool Calling Efficiency for Chip Design Using NVIDIA NeMo Gym** (NVIDIA)

## Key Takeaways
- Tool-calling reliability is now a measured target, not a hope.`
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
