import { Link } from 'react-router-dom';
import {
  DocumentTextIcon,
  MagnifyingGlassIcon,
  CpuChipIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  BoltIcon,
  ServerStackIcon,
  CircleStackIcon,
  CommandLineIcon,
  ArrowRightIcon,
} from '@heroicons/react/24/outline';

const features = [
  {
    icon: MagnifyingGlassIcon,
    title: 'Semantic Search',
    description:
      'Go beyond keyword matching. Ask natural language questions and get AI-generated answers grounded in your own files.',
  },
  {
    icon: CpuChipIcon,
    title: 'RAG Pipeline',
    description:
      'Production-grade Retrieval-Augmented Generation: ingest, chunk, embed, retrieve, rerank, and generate.',
  },
  {
    icon: ShieldCheckIcon,
    title: 'Private & Secure',
    description:
      'Your documents stay yours. No data leaves your infrastructure — fully self-hosted and under your control.',
  },
  {
    icon: ChartBarIcon,
    title: 'Built-in Observability',
    description:
      'Real-time metrics dashboard, query logging, error tracking, and system health monitoring out of the box.',
  },
  {
    icon: BoltIcon,
    title: 'Lightning Fast',
    description:
      'Intelligent model caching, persistent vector storage, and optimized retrieval for sub-second responses.',
  },
  {
    icon: DocumentTextIcon,
    title: 'Multi-Format Support',
    description:
      'Upload PDFs, Markdown, and text files. The system handles chunking, embedding, and indexing automatically.',
  },
];

const techStack = [
  { icon: CommandLineIcon, label: 'React 19 + TypeScript + Vite', category: 'Frontend' },
  { icon: ServerStackIcon, label: 'Python 3.12 + FastAPI', category: 'Backend' },
  { icon: CircleStackIcon, label: 'ChromaDB + Supabase', category: 'Database' },
  { icon: CpuChipIcon, label: 'Groq LLM + Sentence Transformers', category: 'AI Models' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-primary-900">
        {/* Background decoration */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-white rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-secondary-400 rounded-full blur-3xl" />
        </div>

        <nav className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-white">AskMyDoc</h1>
            <Link
              to="/app"
              className="text-sm font-medium text-primary-100 hover:text-white transition-colors"
            >
              Go to App
            </Link>
          </div>
        </nav>

        <div className="relative mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-20 sm:py-28 lg:py-36 text-center">
          <h2 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white leading-tight tracking-tight">
            Stop Digging Through Folders
          </h2>
          <p className="mt-6 max-w-3xl mx-auto text-lg sm:text-xl text-primary-100 leading-relaxed">
            Turn your personal files into a private search engine. Ask natural language questions
            and get AI-generated answers grounded in your own PDFs, Markdown, and text files.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/app"
              className="inline-flex items-center justify-center gap-2 px-8 py-4 text-lg font-semibold text-primary-700 bg-white rounded-xl shadow-lg hover:shadow-xl hover:bg-gray-50 transition-all duration-200"
            >
              Try Ask My Doc
              <ArrowRightIcon className="w-5 h-5" />
            </Link>
          </div>
        </div>

        {/* Wave divider */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 80" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full">
            <path
              d="M0 80L60 72C120 64 240 48 360 40C480 32 600 32 720 36C840 40 960 48 1080 52C1200 56 1320 56 1380 56L1440 56V80H1380C1320 80 1200 80 1080 80C960 80 840 80 720 80C600 80 480 80 360 80C240 80 120 80 60 80H0Z"
              fill="#f9fafb"
            />
          </svg>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 sm:py-28">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Your Documents, Supercharged
            </h3>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              AskMyDoc combines cutting-edge AI with a production-grade architecture to give your
              files a voice.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="bg-white rounded-xl p-8 shadow-sm border border-gray-100 hover:shadow-md hover:border-primary-100 transition-all duration-200"
              >
                <div className="w-12 h-12 rounded-lg bg-primary-50 flex items-center justify-center mb-5">
                  <feature.icon className="w-6 h-6 text-primary-600" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900 mb-2">{feature.title}</h4>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h3 className="text-3xl sm:text-4xl font-bold text-gray-900">How It Works</h3>
            <p className="mt-4 text-lg text-gray-600">Three simple steps to unlock your documents</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              {
                step: '01',
                title: 'Upload Your Documents',
                description:
                  'Drag and drop your PDFs, Markdown notes, or text files. The system automatically chunks and embeds your content into a vector database.',
              },
              {
                step: '02',
                title: 'Ask Questions',
                description:
                  'Type natural language questions about your documents. The RAG pipeline retrieves the most relevant context and generates precise answers.',
              },
              {
                step: '03',
                title: 'Get Grounded Answers',
                description:
                  'Receive AI-generated answers with source citations. Every response is grounded in your actual documents — no hallucinations.',
              },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 text-primary-700 text-2xl font-bold mb-6">
                  {item.step}
                </div>
                <h4 className="text-xl font-semibold text-gray-900 mb-3">{item.title}</h4>
                <p className="text-gray-600 leading-relaxed">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Overview / About Section */}
      <section className="py-20 bg-gray-50">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <div className="prose prose-lg max-w-none">
            <h3 className="text-3xl sm:text-4xl font-bold text-gray-900 text-center mb-12">
              About AskMyDoc
            </h3>

            <div className="space-y-8 text-gray-700 leading-relaxed">
              <p>
                Many of us suffer from "digital hoarding," accumulating hundreds of PDFs, Markdown
                notes, and text files that eventually vanish into a desktop graveyard of nested
                folders. When you actually need a specific piece of information, standard keyword
                searching often fails to find the context you require. <strong>AskMyDoc</strong> is
                a production-grade Retrieval-Augmented Generation (RAG) system that gives your
                personal documents a "voice," transforming them into a private, locally hosted search
                engine.
              </p>

              <div className="bg-white rounded-xl p-8 border border-gray-200">
                <h4 className="text-xl font-semibold text-gray-900 mb-4">
                  RAG: Giving Your Documents an Instant Upgrade
                </h4>
                <p>
                  While traditional search tools rely on exact string matching — which often misses
                  the "intent" behind a query — RAG enables semantic Q&A. AskMyDoc eliminates the
                  limitations of static storage through "Vector Search" powered by ChromaDB. By
                  converting your text into mathematical vectors, the system captures the "essence"
                  and conceptual meaning of your data rather than just matching characters.
                </p>
              </div>

              <div className="bg-white rounded-xl p-8 border border-gray-200">
                <h4 className="text-xl font-semibold text-gray-900 mb-4">
                  Transparency and System Observability
                </h4>
                <p>
                  The inclusion of a relational database is a defining feature that elevates AskMyDoc
                  beyond a standard coding script. By using Supabase (managed PostgreSQL) to log
                  queries and errors, the system provides a robust audit trail and true system
                  observability. The built-in Metrics Dashboard lets you monitor system performance
                  in real-time, providing a window into the AI's "thought process."
                </p>
              </div>

              <div className="bg-white rounded-xl p-8 border border-gray-200">
                <h4 className="text-xl font-semibold text-gray-900 mb-4">
                  Efficiency and the "Set It and Forget It" Model
                </h4>
                <p>
                  Performance is optimized through intelligent model caching and persistent
                  environments. While the first run may take a moment to load the AI models, all
                  subsequent uses are significantly faster because models are cached locally. This
                  "set it and forget it" approach makes the tool feel like a native part of your
                  workflow rather than a fragile experimental script.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tech Stack Section */}
      <section className="py-20 bg-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Production-Grade Tech Stack
            </h3>
            <p className="mt-4 text-lg text-gray-600">
              Built with industry-standard tools for reliability and speed
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {techStack.map((tech) => (
              <div
                key={tech.category}
                className="bg-gray-50 rounded-xl p-6 text-center border border-gray-100"
              >
                <tech.icon className="w-8 h-8 text-primary-600 mx-auto mb-3" />
                <p className="text-xs font-medium text-primary-600 uppercase tracking-wide mb-1">
                  {tech.category}
                </p>
                <p className="text-sm font-medium text-gray-900">{tech.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-primary-600 to-primary-800">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Your Documents, Democratized
          </h3>
          <p className="text-lg text-primary-100 mb-4 max-w-2xl mx-auto leading-relaxed">
            AskMyDoc represents a fundamental shift toward local, private AI ownership. Combine
            FastAPI, React, and RAG technology to reclaim your data and put it to work.
          </p>
          <p className="text-primary-200 italic mb-10">
            If you could talk to every document you've ever written, what's the first question you
            would ask your past self?
          </p>
          <Link
            to="/app"
            className="inline-flex items-center justify-center gap-2 px-10 py-4 text-lg font-semibold text-primary-700 bg-white rounded-xl shadow-lg hover:shadow-xl hover:bg-gray-50 transition-all duration-200"
          >
            Try Ask My Doc
            <ArrowRightIcon className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 py-8">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400 text-sm">
            AskMyDoc — Production-Grade RAG System
          </p>
        </div>
      </footer>
    </div>
  );
}
