import {useEffect, useState} from 'react';
import {Check, Copy, FileText} from 'lucide-react';

export function ReadmeViewer() {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch('/api/jarvis/file?path=README.md')
      .then((res) => {
        if (!res.ok) throw new Error('Unable to load JARVIS/README.md');
        return res.json();
      })
      .then((data) => {
        if (!cancelled) setContent(data.content ?? '');
      })
      .catch((err) => {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load README');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-slate-100">
            JARVIS Complete README &amp; Operator Guide
          </h2>
          <p className="mt-1 text-sm text-slate-400">
            Live contents of <span className="font-mono text-slate-200">JARVIS/README.md</span> — covers Discord Portal setup, Windows/Linux Mint/Docker execution, commands, and troubleshooting.
          </p>
        </div>

        <button
          type="button"
          onClick={handleCopy}
          disabled={!content}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 bg-[#0F172A] px-3.5 py-2 text-xs font-medium text-slate-200 transition-colors hover:bg-slate-800 disabled:opacity-40 whitespace-nowrap shrink-0"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
          {copied ? 'Copied README' : 'Copy README'}
        </button>
      </div>

      {/* Quick Reference Summary */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-4">
          <h3 className="text-sm font-semibold text-slate-100">1. Configure &amp; Invite</h3>
          <p className="mt-1.5 text-xs leading-relaxed text-slate-400">
            Enable Presence, Server Members, and Message Content intents in Discord Developer Portal, then copy <span className="font-mono text-slate-200">.env.example</span> to <span className="font-mono text-slate-200">.env</span> and set <span className="font-mono text-slate-200">DISCORD_TOKEN</span>.
          </p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-4">
          <h3 className="text-sm font-semibold text-slate-100">2. Migrate &amp; Run</h3>
          <p className="mt-1.5 text-xs leading-relaxed text-slate-400">
            Activate Python venv, install <span className="font-mono text-slate-200">requirements.txt</span>, run <span className="font-mono text-slate-200">alembic upgrade head</span>, and start <span className="font-mono text-slate-200">python bot.py</span> (or use <span className="font-mono text-slate-200">scripts/start.*</span>).
          </p>
        </div>
        <div className="rounded-xl border border-slate-800 bg-[#0F172A] p-4">
          <h3 className="text-sm font-semibold text-slate-100">3. Sync &amp; Use</h3>
          <p className="mt-1.5 text-xs leading-relaxed text-slate-400">
            Run <span className="font-mono text-slate-200">j!sync guild</span> as Bot Owner to register slash commands, then use <span className="font-mono text-slate-200">/help</span> or <span className="font-mono text-slate-200">j!help</span> to explore modules.
          </p>
        </div>
      </div>

      <div className="rounded-xl border border-slate-800 bg-[#0F172A]">
        <div className="flex items-center gap-2 border-b border-slate-800 px-4 py-3">
          <FileText className="h-4 w-4 text-sky-400" />
          <span className="font-mono text-xs text-slate-200">JARVIS/README.md</span>
        </div>

        <div className="p-5">
          {loading ? (
            <div className="space-y-2">
              <div className="h-4 w-1/2 animate-pulse rounded bg-slate-800/60" />
              <div className="h-4 w-3/4 animate-pulse rounded bg-slate-800/60" />
              <div className="h-4 w-2/3 animate-pulse rounded bg-slate-800/60" />
            </div>
          ) : error ? (
            <p className="text-xs text-red-400">{error}</p>
          ) : (
            <pre className="max-h-[600px] overflow-auto whitespace-pre-wrap font-mono text-xs leading-relaxed text-slate-300">
              {content}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
