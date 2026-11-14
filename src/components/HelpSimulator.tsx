import {useState} from 'react';
import {ChevronLeft, ChevronRight, Home, Search} from 'lucide-react';
import {MODULE_SPECS, PHASE1_COMMANDS} from '../data/jarvisArchitecture';

export function HelpSimulator() {
  const [selectedCategory, setSelectedCategory] = useState<string>('overview');
  const [page, setPage] = useState<number>(0);
  const [searchOpen, setSearchOpen] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>('');

  const pageSize = 4;
  const categoryCommands =
    selectedCategory === 'overview'
      ? []
      : PHASE1_COMMANDS.filter((c) => c.category === selectedCategory);
  const totalPages = Math.max(1, Math.ceil(categoryCommands.length / pageSize));
  const pagedCommands = categoryCommands.slice(page * pageSize, page * pageSize + pageSize);

  const searchMatches = searchQuery.trim()
    ? PHASE1_COMMANDS.filter(
        (c) =>
          c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.aliases.some((a) => a.toLowerCase().includes(searchQuery.toLowerCase()))
      )
    : [];

  const activeModule = MODULE_SPECS.find((m) => m.name === selectedCategory);

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
      <div className="lg:col-span-7 rounded-xl border border-slate-800 bg-[#0F172A] p-5">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold text-slate-100">
              Interactive Discord Help Menu Preview
            </h2>
            <p className="text-xs text-slate-400">
              Mirrors <span className="font-mono text-slate-300">cogs/general/help.py</span> — introspects live commands only.
            </p>
          </div>
          <span className="font-mono text-xs text-slate-400 tabular-nums">
            {PHASE1_COMMANDS.length} live cmds
          </span>
        </div>

        {/* Simulated Discord Embed */}
        <div className="rounded-lg border border-slate-800 bg-[#1E222B] p-4 shadow-sm">
          <div className="flex items-start justify-between gap-4 border-b border-slate-700/60 pb-3">
            <div>
              <h3 className="text-sm font-semibold text-sky-300">
                {selectedCategory === 'overview'
                  ? 'JARVIS Command Matrix'
                  : `JARVIS — ${selectedCategory} Module`}
              </h3>
              <p className="mt-1 text-xs leading-relaxed text-slate-300">
                {selectedCategory === 'overview'
                  ? 'Advanced All-In-One Discord Management Bot. Select any of the 17 modules from the dropdown below or click Search.'
                  : activeModule?.description}
              </p>
            </div>
          </div>

          <div className="mt-4">
            {selectedCategory === 'overview' ? (
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
                {MODULE_SPECS.map((mod) => {
                  const cmdCount = PHASE1_COMMANDS.filter((c) => c.category === mod.name).length;
                  return (
                    <button
                      key={mod.id}
                      type="button"
                      onClick={() => {
                        setSelectedCategory(mod.name);
                        setPage(0);
                      }}
                      className="flex items-center justify-between rounded-md border border-slate-700/60 bg-[#252A34] px-3 py-2 text-left text-xs transition-colors hover:border-sky-500/60"
                    >
                      <span className="font-medium text-slate-200">
                        {String(mod.id).padStart(2, '0')}. {mod.name}
                      </span>
                      <span className="font-mono text-slate-400 tabular-nums">
                        {cmdCount > 0 ? `${cmdCount} cmds` : `Phase ${mod.phase}`}
                      </span>
                    </button>
                  );
                })}
              </div>
            ) : pagedCommands.length > 0 ? (
              <div className="space-y-3">
                {pagedCommands.map((cmd) => (
                  <div
                    key={cmd.name}
                    className="rounded-md border border-slate-700/60 bg-[#252A34] p-3"
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-mono text-xs font-semibold text-sky-300">
                        /{cmd.name} · {cmd.usage}
                      </span>
                      <span className="text-xs text-slate-400">Perms: {cmd.permissions}</span>
                    </div>
                    <p className="mt-1 text-xs text-slate-300">{cmd.description}</p>
                    <p className="mt-1 font-mono text-[11px] text-slate-400">
                      Aliases: {cmd.aliases.length > 0 ? cmd.aliases.join(', ') : 'None'}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="rounded-md border border-slate-700/60 bg-[#252A34] p-4 text-xs text-slate-300">
                The <span className="font-semibold text-white">{selectedCategory}</span> module is scheduled for{' '}
                <span className="font-semibold text-sky-300">Phase {activeModule?.phase}</span>. Zero placeholder commands are displayed until its Cog is loaded.
              </div>
            )}
          </div>

          <div className="mt-4 border-t border-slate-700/60 pt-2.5 text-[11px] text-slate-400">
            JARVIS • Developed by Shadow · Page {page + 1}/{totalPages}
          </div>
        </div>

        {/* Simulated Discord Components (Select + Action Row) */}
        <div className="mt-3 space-y-2.5">
          <select
            aria-label="Select JARVIS module category"
            value={selectedCategory}
            onChange={(e) => {
              setSelectedCategory(e.target.value);
              setPage(0);
            }}
            className="w-full rounded-lg border border-slate-700 bg-[#0B1120] px-3 py-2 text-xs text-slate-200 focus:border-sky-500 focus:outline-none"
          >
            <option value="overview">Overview — 17 Module Directory</option>
            {MODULE_SPECS.map((mod) => (
              <option key={mod.id} value={mod.name}>
                {mod.name} (Phase {mod.phase})
              </option>
            ))}
          </select>

          <div className="flex flex-wrap items-center gap-2">
            <button
              type="button"
              disabled={selectedCategory === 'overview' || page <= 0}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              className="inline-flex items-center gap-1 rounded-md bg-slate-700 px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40 whitespace-nowrap shrink-0"
            >
              <ChevronLeft className="h-3.5 w-3.5" />
              Previous
            </button>
            <button
              type="button"
              disabled={selectedCategory === 'overview'}
              onClick={() => {
                setSelectedCategory('overview');
                setPage(0);
              }}
              className="inline-flex items-center gap-1 rounded-md bg-sky-600 px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40 whitespace-nowrap shrink-0"
            >
              <Home className="h-3.5 w-3.5" />
              Home
            </button>
            <button
              type="button"
              disabled={selectedCategory === 'overview' || page >= totalPages - 1}
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              className="inline-flex items-center gap-1 rounded-md bg-slate-700 px-3 py-1.5 text-xs font-medium text-white disabled:opacity-40 whitespace-nowrap shrink-0"
            >
              Next
              <ChevronRight className="h-3.5 w-3.5" />
            </button>
            <button
              type="button"
              onClick={() => setSearchOpen((prev) => !prev)}
              className="inline-flex items-center gap-1 rounded-md bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white whitespace-nowrap shrink-0"
            >
              <Search className="h-3.5 w-3.5" />
              Search
            </button>
          </div>

          {searchOpen && (
            <div className="rounded-lg border border-slate-700 bg-[#0B1120] p-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search live commands (e.g. prefix, ping, botinfo)..."
                className="w-full rounded-md border border-slate-700 bg-[#0F172A] px-3 py-1.5 text-xs text-slate-200 focus:border-sky-500 focus:outline-none"
              />
              <div className="mt-2 space-y-1.5">
                {!searchQuery.trim() ? (
                  <p className="text-xs text-slate-500">Type a command name or alias to search.</p>
                ) : searchMatches.length === 0 ? (
                  <p className="text-xs text-amber-400">No loaded command matched "{searchQuery}".</p>
                ) : (
                  searchMatches.map((m) => (
                    <div key={m.name} className="rounded bg-slate-800/70 px-2.5 py-1.5 text-xs">
                      <span className="font-mono font-semibold text-sky-300">{m.usage}</span>
                      <span className="ml-2 text-slate-300">{m.description}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Setup & Run Instructions */}
      <div className="lg:col-span-5 space-y-4">
        <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-5">
          <h3 className="text-sm font-semibold text-slate-100">
            Discord Developer Portal Requirements
          </h3>
          <ul className="mt-3 space-y-2 text-xs text-slate-300">
            <li>1. Create application named <strong className="text-white">JARVIS</strong>.</li>
            <li>2. Enable Privileged Intents: Presence, Server Members, and Message Content.</li>
            <li>3. Add OAuth2 redirect URL for the FastAPI dashboard (<span className="font-mono text-slate-200">/auth/callback</span>).</li>
            <li>4. Invite with scopes <span className="font-mono text-slate-200">bot</span> and <span className="font-mono text-slate-200">applications.commands</span>.</li>
          </ul>
        </div>

        <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-5">
          <h3 className="text-sm font-semibold text-slate-100">Quick Launch Commands</h3>
          <div className="mt-3 space-y-3 text-xs">
            <div>
              <p className="mb-1 font-medium text-slate-300">Windows (CMD / PowerShell)</p>
              <pre className="overflow-x-auto rounded-lg border border-slate-800 bg-[#0B1120] p-2.5 font-mono text-[11px] text-slate-300">
{`cd JARVIS
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
alembic upgrade head
python bot.py`}
              </pre>
            </div>
            <div>
              <p className="mb-1 font-medium text-slate-300">Linux / Linux Mint</p>
              <pre className="overflow-x-auto rounded-lg border border-slate-800 bg-[#0B1120] p-2.5 font-mono text-[11px] text-slate-300">
{`cd JARVIS
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python bot.py`}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
