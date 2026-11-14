import {useState} from 'react';
import {Search} from 'lucide-react';
import {ALL_23_MODEL_NAMES, DATABASE_MODELS} from '../data/jarvisArchitecture';

export function SchemaExplorer() {
  const [query, setQuery] = useState('');

  const filtered = DATABASE_MODELS.filter(
    (m) =>
      m.table.toLowerCase().includes(query.toLowerCase()) ||
      m.model.toLowerCase().includes(query.toLowerCase()) ||
      m.module.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-100">
            SQLAlchemy Async ORM &amp; Alembic Schema
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            23 normalized tables defined in <span className="font-mono text-slate-200">JARVIS/database/models.py</span> supporting SQLite (WAL mode) locally and PostgreSQL 16 in production.
          </p>
        </div>

        <div className="relative w-full sm:w-72">
          <Search className="pointer-events-none absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search tables or modules..."
            className="w-full rounded-lg border border-slate-800 bg-[#0F172A] py-2 pl-9 pr-3 text-xs text-slate-200 placeholder-slate-500 focus:border-sky-500 focus:outline-none"
          />
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-4">
        <p className="mb-2 text-xs font-medium text-slate-400">All 23 Registered ORM Models</p>
        <p className="font-mono text-xs leading-6 text-slate-300">
          {ALL_23_MODEL_NAMES.join(' · ')}
        </p>
      </div>

      {filtered.length === 0 ? (
        <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-8 text-center">
          <p className="text-sm text-slate-400">No detailed schema preview matched "{query}".</p>
          <button
            type="button"
            onClick={() => setQuery('')}
            className="mt-3 rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-slate-800"
          >
            Reset Filter
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {filtered.map((schema) => (
            <div key={schema.table} className="rounded-xl border border-slate-800 bg-[#0F172A] p-4">
              <div className="mb-3 flex items-baseline justify-between gap-4 border-b border-slate-800 pb-2.5">
                <div>
                  <h3 className="font-mono text-sm font-semibold text-sky-300">{schema.model}</h3>
                  <p className="text-xs text-slate-500">
                    Table <span className="font-mono text-slate-400">{schema.table}</span> · {schema.module}
                  </p>
                </div>
                <span className="font-mono text-xs text-slate-500 tabular-nums">
                  {schema.columns.length} cols
                </span>
              </div>

              <div className="space-y-2">
                {schema.columns.map((col) => (
                  <div
                    key={col.name}
                    className="flex items-start justify-between gap-3 text-xs"
                  >
                    <div className="min-w-0">
                      <span className="font-mono text-slate-200">{col.name}</span>
                      <span className="ml-2 text-slate-500">{col.notes}</span>
                    </div>
                    <span className="shrink-0 font-mono text-slate-400">{col.type}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
