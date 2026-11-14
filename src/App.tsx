import {useState} from 'react';
import {
  CheckCircle2,
  Clock,
  Code2,
  Database,
  FileText,
  Layers,
  Shield,
  Terminal,
} from 'lucide-react';
import {HelpSimulator} from './components/HelpSimulator';
import {ReadmeViewer} from './components/ReadmeViewer';
import {SchemaExplorer} from './components/SchemaExplorer';
import {SourceExplorer} from './components/SourceExplorer';
import {MODULE_SPECS, ROADMAP_PHASES} from './data/jarvisArchitecture';

type NavTab = 'overview' | 'readme' | 'source' | 'database' | 'help';

export default function App() {
  const [activeTab, setActiveTab] = useState<NavTab>('overview');
  const [moduleFilter, setModuleFilter] = useState<'all' | 'implemented' | 'pending'>('all');

  const completedPhases = ROADMAP_PHASES.filter((p) => p.status === 'completed').length;
  const activeModules = MODULE_SPECS.filter((m) => m.status === 'implemented').length;
  const filteredModules = MODULE_SPECS.filter((m) =>
    moduleFilter === 'all' ? true : m.status === moduleFilter
  );

  const navItems: {id: NavTab; label: string; icon: typeof Layers}[] = [
    {id: 'overview', label: 'Architecture & Roadmap', icon: Layers},
    {id: 'readme', label: 'README & Guide', icon: FileText},
    {id: 'source', label: 'Python Source Explorer', icon: Code2},
    {id: 'database', label: 'Database Schema', icon: Database},
    {id: 'help', label: 'Help Menu & Setup', icon: Terminal},
  ];

  return (
    <div className="min-h-screen bg-[#0B1120] text-slate-100 lg:flex">
      {/* Sidebar Navigation */}
      <aside className="w-full shrink-0 border-b border-slate-800 bg-[#0F172A] lg:w-[260px] lg:border-b-0 lg:border-r">
        <div className="flex h-16 items-center gap-2.5 border-b border-slate-800 px-5">
          <Shield className="h-5 w-5 text-sky-400" />
          <span className="text-base font-bold tracking-tight text-white whitespace-nowrap">
            JARVIS
          </span>
        </div>

        <nav className="flex gap-1 overflow-x-auto p-3 lg:flex-col">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = activeTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setActiveTab(item.id)}
                className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-left text-xs font-medium transition-colors whitespace-nowrap shrink-0 ${
                  active
                    ? 'bg-sky-500/15 text-sky-300'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-100'
                }`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="hidden border-t border-slate-800 p-4 text-xs text-slate-400 lg:block">
          <p className="font-medium text-slate-200">Project Identity</p>
          <p className="mt-1.5">Bot Name · JARVIS</p>
          <p>Developer · Shadow</p>
          <p>Stack · Python 3.12 / discord.py 2.x</p>
          <p>DB · SQLite &amp; PostgreSQL</p>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 min-w-0">
        {/* Top Bar Contract */}
        <header className="flex h-16 items-center justify-between gap-8 border-b border-slate-800 bg-[#0F172A]/80 px-6">
          <div className="flex items-center gap-2 text-xs text-slate-400 min-w-0">
            <span className="truncate font-medium text-slate-200">JARVIS Workspace</span>
            <span aria-hidden="true">/</span>
            <span className="truncate text-slate-400">
              {navItems.find((n) => n.id === activeTab)?.label}
            </span>
          </div>

          <button
            type="button"
            onClick={() => setActiveTab('source')}
            className="rounded-lg bg-sky-600 px-4 py-2 text-xs font-medium text-white transition-colors hover:bg-sky-500 whitespace-nowrap shrink-0"
          >
            Inspect Python Code
          </button>
        </header>

        <main className="mx-auto max-w-[1200px] p-6">
          {activeTab === 'overview' && (
            <div className="space-y-8">
              <div>
                <h1 className="text-2xl font-bold tracking-tight text-white">
                  JARVIS — Advanced All-In-One Discord Management Bot
                </h1>
                <p className="mt-2 max-w-3xl text-sm leading-relaxed text-slate-400">
                  Pure Python modular architecture built on <span className="font-mono text-slate-200">discord.py 2.x</span>,{' '}
                  <span className="font-mono text-slate-200">SQLAlchemy Async</span>,{' '}
                  <span className="font-mono text-slate-200">Alembic</span>,{' '}
                  <span className="font-mono text-slate-200">Wavelink (Lavalink v4)</span>, and{' '}
                  <span className="font-mono text-slate-200">FastAPI</span>. Developed by Shadow.
                </p>
              </div>

              {/* 4-column summary strip */}
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-4">
                  <p className="text-xs text-slate-400">Roadmap Progress</p>
                  <p className="mt-1 font-mono text-xl font-semibold text-white tabular-nums">
                    {completedPhases} / {ROADMAP_PHASES.length} Phases
                  </p>
                </div>
                <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-4">
                  <p className="text-xs text-slate-400">Target Modules</p>
                  <p className="mt-1 font-mono text-xl font-semibold text-white tabular-nums">
                    {activeModules} / 17 Active
                  </p>
                </div>
                <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-4">
                  <p className="text-xs text-slate-400">ORM Data Models</p>
                  <p className="mt-1 font-mono text-xl font-semibold text-white tabular-nums">
                    23 Tables
                  </p>
                </div>
                <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-4">
                  <p className="text-xs text-slate-400">Python Runtime</p>
                  <p className="mt-1 font-mono text-xl font-semibold text-white tabular-nums">
                    3.12+ / 3.13
                  </p>
                </div>
              </div>

              {/* Development Roadmap Checklist */}
              <section className="space-y-3">
                <h2 className="text-base font-semibold text-slate-100">
                  Development Roadmap &amp; Phase Checklist
                </h2>
                <div className="divide-y divide-slate-800 rounded-xl border border-slate-800 bg-[#0F172A]">
                  {ROADMAP_PHASES.map((phase) => {
                    const isDone = phase.status === 'completed';
                    return (
                      <div key={phase.id} className="p-4">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex items-center gap-2.5">
                            {isDone ? (
                              <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400" />
                            ) : (
                              <Clock className="h-4 w-4 shrink-0 text-slate-500" />
                            )}
                            <h3 className="text-sm font-semibold text-slate-100">{phase.name}</h3>
                          </div>
                          <span
                            className={`text-xs font-medium ${
                              isDone ? 'text-emerald-400' : 'text-slate-400'
                            }`}
                          >
                            {isDone ? 'Completed & Syntax Verified' : 'Pending'}
                          </span>
                        </div>
                        <p className="mt-1.5 text-xs leading-relaxed text-slate-400">
                          {phase.summary}
                        </p>
                        <ul className="mt-2.5 grid grid-cols-1 gap-1 text-xs text-slate-300 md:grid-cols-2">
                          {phase.deliverables.map((item) => (
                            <li key={item} className="truncate font-mono text-[11px] text-slate-400">
                              · {item}
                            </li>
                          ))}
                        </ul>
                      </div>
                    );
                  })}
                </div>
              </section>

              {/* 17 Modules Matrix */}
              <section className="space-y-3">
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <h2 className="text-base font-semibold text-slate-100">
                    17 Official JARVIS Modules
                  </h2>
                  <div className="flex items-center gap-1 rounded-lg bg-[#0F172A] p-1 border border-slate-800">
                    {(['all', 'implemented', 'pending'] as const).map((tab) => (
                      <button
                        key={tab}
                        type="button"
                        onClick={() => setModuleFilter(tab)}
                        className={`rounded-md px-3 py-1 text-xs font-medium capitalize transition-colors whitespace-nowrap shrink-0 ${
                          moduleFilter === tab
                            ? 'bg-sky-600 text-white'
                            : 'text-slate-400 hover:text-white'
                        }`}
                      >
                        {tab}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
                  {filteredModules.map((mod) => (
                    <div
                      key={mod.id}
                      className="rounded-xl border border-slate-800 bg-[#0F172A] p-4"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <h3 className="text-sm font-semibold text-slate-100">
                          {String(mod.id).padStart(2, '0')}. {mod.name}
                        </h3>
                        <span
                          className={`text-xs font-medium ${
                            mod.status === 'implemented' ? 'text-emerald-400' : 'text-slate-500'
                          }`}
                        >
                          {mod.status === 'implemented' ? 'Active (Phase 1)' : `Phase ${mod.phase}`}
                        </span>
                      </div>
                      <p className="mt-1.5 text-xs leading-relaxed text-slate-400">
                        {mod.description}
                      </p>
                      <p className="mt-2.5 text-[11px] text-slate-500">
                        {mod.keyFeatures.join(' · ')}
                      </p>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          )}

          {activeTab === 'readme' && <ReadmeViewer />}
          {activeTab === 'source' && <SourceExplorer />}
          {activeTab === 'database' && <SchemaExplorer />}
          {activeTab === 'help' && <HelpSimulator />}
        </main>
      </div>
    </div>
  );
}
