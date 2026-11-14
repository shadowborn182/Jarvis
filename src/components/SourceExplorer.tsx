import {useEffect, useState} from 'react';
import {Check, ChevronDown, ChevronRight, Copy, FileCode2, Folder, RefreshCw, Search} from 'lucide-react';

interface WorkspaceNode {
  name: string;
  path: string;
  type: 'file' | 'dir';
  size?: number;
  children?: WorkspaceNode[];
}

function flattenFiles(nodes: WorkspaceNode[]): WorkspaceNode[] {
  const out: WorkspaceNode[] = [];
  for (const node of nodes) {
    if (node.type === 'file') out.push(node);
    if (node.children) out.push(...flattenFiles(node.children));
  }
  return out;
}

function TreeBranch({
  nodes,
  selectedPath,
  onSelect,
  expandedDirs,
  toggleDir,
  depth = 0,
}: {
  nodes: WorkspaceNode[];
  selectedPath: string;
  onSelect: (path: string) => void;
  expandedDirs: Set<string>;
  toggleDir: (path: string) => void;
  depth?: number;
}) {
  return (
    <ul className="space-y-0.5">
      {nodes.map((node) => {
        if (node.type === 'dir') {
          const isOpen = expandedDirs.has(node.path);
          return (
            <li key={node.path}>
              <button
                type="button"
                onClick={() => toggleDir(node.path)}
                style={{paddingLeft: `${depth * 14 + 8}px`}}
                className="flex w-full items-center gap-2 rounded-md py-1.5 pr-2 text-left text-xs font-medium text-slate-300 transition-colors hover:bg-slate-800/70 hover:text-white"
              >
                {isOpen ? (
                  <ChevronDown className="h-3.5 w-3.5 shrink-0 text-slate-500" />
                ) : (
                  <ChevronRight className="h-3.5 w-3.5 shrink-0 text-slate-500" />
                )}
                <Folder className="h-3.5 w-3.5 shrink-0 text-sky-400" />
                <span className="truncate">{node.name}</span>
              </button>
              {isOpen && node.children && (
                <TreeBranch
                  nodes={node.children}
                  selectedPath={selectedPath}
                  onSelect={onSelect}
                  expandedDirs={expandedDirs}
                  toggleDir={toggleDir}
                  depth={depth + 1}
                />
              )}
            </li>
          );
        }

        const active = selectedPath === node.path;
        return (
          <li key={node.path}>
            <button
              type="button"
              onClick={() => onSelect(node.path)}
              style={{paddingLeft: `${depth * 14 + 24}px`}}
              className={`flex w-full items-center gap-2 rounded-md py-1.5 pr-2 text-left text-xs transition-colors ${
                active
                  ? 'bg-sky-500/15 font-medium text-sky-300'
                  : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
              }`}
            >
              <FileCode2 className="h-3.5 w-3.5 shrink-0 opacity-75" />
              <span className="truncate font-mono">{node.name}</span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}

export function SourceExplorer() {
  const [tree, setTree] = useState<WorkspaceNode[]>([]);
  const [selectedPath, setSelectedPath] = useState<string>('bot.py');
  const [fileContent, setFileContent] = useState<string>('');
  const [filterText, setFilterText] = useState<string>('');
  const [loadingTree, setLoadingTree] = useState<boolean>(true);
  const [loadingFile, setLoadingFile] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);
  const [expandedDirs, setExpandedDirs] = useState<Set<string>>(
    () => new Set(['core', 'cogs', 'cogs/general', 'database', 'tests', 'scripts'])
  );

  const loadTree = async () => {
    setLoadingTree(true);
    setError(null);
    try {
      const res = await fetch('/api/jarvis/tree');
      if (!res.ok) throw new Error('Unable to read JARVIS workspace tree.');
      const data = await res.json();
      setTree(data.tree ?? []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load file tree.');
    } finally {
      setLoadingTree(false);
    }
  };

  useEffect(() => {
    void loadTree();
  }, []);

  useEffect(() => {
    if (!selectedPath) return;
    let cancelled = false;
    setLoadingFile(true);
    fetch(`/api/jarvis/file?path=${encodeURIComponent(selectedPath)}`)
      .then((res) => {
        if (!res.ok) throw new Error('File could not be loaded.');
        return res.json();
      })
      .then((data) => {
        if (!cancelled) setFileContent(data.content ?? '');
      })
      .catch(() => {
        if (!cancelled) setFileContent('# Unable to load file content.');
      })
      .finally(() => {
        if (!cancelled) setLoadingFile(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedPath]);

  const toggleDir = (dirPath: string) => {
    setExpandedDirs((prev) => {
      const next = new Set(prev);
      if (next.has(dirPath)) next.delete(dirPath);
      else next.add(dirPath);
      return next;
    });
  };

  const handleCopy = async () => {
    await navigator.clipboard.writeText(fileContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };

  const allFiles = flattenFiles(tree);
  const filteredFiles = filterText.trim()
    ? allFiles.filter((f) => f.path.toLowerCase().includes(filterText.trim().toLowerCase()))
    : null;

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
      <div className="lg:col-span-4 rounded-xl border border-slate-800 bg-[#0F172A] p-4">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-100">JARVIS File Tree</h3>
          <button
            type="button"
            onClick={loadTree}
            className="inline-flex items-center gap-1.5 rounded-md border border-slate-700 px-2.5 py-1 text-xs font-medium text-slate-300 transition-colors hover:bg-slate-800 hover:text-white whitespace-nowrap shrink-0"
          >
            <RefreshCw className="h-3 w-3" />
            Refresh
          </button>
        </div>

        <div className="relative mb-3">
          <Search className="pointer-events-none absolute left-3 top-2.5 h-3.5 w-3.5 text-slate-500" />
          <input
            type="text"
            value={filterText}
            onChange={(e) => setFilterText(e.target.value)}
            placeholder="Filter files..."
            className="w-full rounded-lg border border-slate-800 bg-[#0B1120] py-1.5 pl-8 pr-3 text-xs text-slate-200 placeholder-slate-500 focus:border-sky-500 focus:outline-none"
          />
        </div>

        {loadingTree ? (
          <div className="space-y-2 py-4">
            <div className="h-6 animate-pulse rounded bg-slate-800/60" />
            <div className="h-6 animate-pulse rounded bg-slate-800/60" />
            <div className="h-6 animate-pulse rounded bg-slate-800/60" />
          </div>
        ) : error ? (
          <p className="py-4 text-xs text-red-400">{error}</p>
        ) : filteredFiles ? (
          <ul className="max-h-[540px] space-y-1 overflow-y-auto">
            {filteredFiles.length === 0 ? (
              <li className="py-4 text-xs text-slate-500">No files match "{filterText}".</li>
            ) : (
              filteredFiles.map((file) => (
                <li key={file.path}>
                  <button
                    type="button"
                    onClick={() => setSelectedPath(file.path)}
                    className={`flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-left font-mono text-xs transition-colors ${
                      selectedPath === file.path
                        ? 'bg-sky-500/15 text-sky-300'
                        : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                    }`}
                  >
                    <FileCode2 className="h-3.5 w-3.5 shrink-0" />
                    <span className="truncate">{file.path}</span>
                  </button>
                </li>
              ))
            )}
          </ul>
        ) : (
          <div className="max-h-[540px] overflow-y-auto pr-1">
            <TreeBranch
              nodes={tree}
              selectedPath={selectedPath}
              onSelect={setSelectedPath}
              expandedDirs={expandedDirs}
              toggleDir={toggleDir}
            />
          </div>
        )}
      </div>

      <div className="lg:col-span-8 flex flex-col rounded-xl border border-slate-800 bg-[#0F172A]">
        <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
          <div className="min-w-0">
            <p className="truncate font-mono text-xs text-slate-200">JARVIS/{selectedPath}</p>
            <p className="text-xs text-slate-500 tabular-nums">
              {fileContent.split('\n').length} lines
            </p>
          </div>
          <button
            type="button"
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/60 px-3 py-1.5 text-xs font-medium text-slate-200 transition-colors hover:bg-slate-800 whitespace-nowrap shrink-0"
          >
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
            {copied ? 'Copied' : 'Copy Code'}
          </button>
        </div>

        <div className="flex-1 overflow-auto p-4">
          {loadingFile ? (
            <div className="space-y-2">
              <div className="h-4 w-2/3 animate-pulse rounded bg-slate-800/60" />
              <div className="h-4 w-5/6 animate-pulse rounded bg-slate-800/60" />
              <div className="h-4 w-1/2 animate-pulse rounded bg-slate-800/60" />
            </div>
          ) : (
            <pre className="max-h-[560px] overflow-auto font-mono text-xs leading-relaxed text-slate-300">
              <code>{fileContent}</code>
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
