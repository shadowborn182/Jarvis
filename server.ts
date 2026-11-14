import express from 'express';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const JARVIS_ROOT = path.resolve(__dirname, 'JARVIS');

interface WorkspaceNode {
  name: string;
  path: string;
  type: 'file' | 'dir';
  size?: number;
  children?: WorkspaceNode[];
}

async function scanJarvisTree(dir: string, relBase = ''): Promise<WorkspaceNode[]> {
  let entries;
  try {
    entries = await fs.readdir(dir, {withFileTypes: true});
  } catch {
    return [];
  }

  const ignored = new Set(['__pycache__', '.venv', '.pytest_cache', 'node_modules']);
  const nodes: WorkspaceNode[] = [];

  for (const entry of entries) {
    if (ignored.has(entry.name)) continue;
    const fullPath = path.join(dir, entry.name);
    const relPath = relBase ? `${relBase}/${entry.name}` : entry.name;

    if (entry.isDirectory()) {
      const children = await scanJarvisTree(fullPath, relPath);
      nodes.push({name: entry.name, path: relPath, type: 'dir', children});
    } else if (entry.isFile()) {
      const stat = await fs.stat(fullPath);
      nodes.push({name: entry.name, path: relPath, type: 'file', size: stat.size});
    }
  }

  return nodes.sort((a, b) => {
    if (a.type !== b.type) return a.type === 'dir' ? -1 : 1;
    return a.name.localeCompare(b.name);
  });
}

async function createServer() {
  const app = express();
  const port = Number(process.env.PORT) || 3000;

  app.get('/api/jarvis/tree', async (_req, res) => {
    const tree = await scanJarvisTree(JARVIS_ROOT);
    res.json({root: 'JARVIS', tree});
  });

  app.get('/api/jarvis/file', async (req, res) => {
    const relPath = typeof req.query.path === 'string' ? req.query.path : '';
    if (!relPath) {
      res.status(400).json({error: 'Missing file path parameter.'});
      return;
    }

    const resolved = path.resolve(JARVIS_ROOT, relPath);
    if (!resolved.startsWith(JARVIS_ROOT + path.sep)) {
      res.status(403).json({error: 'Access denied outside JARVIS workspace.'});
      return;
    }

    try {
      const content = await fs.readFile(resolved, 'utf-8');
      res.json({path: relPath, content});
    } catch {
      res.status(404).json({error: 'File not found.'});
    }
  });

  const isProd = process.env.NODE_ENV === 'production';
  if (!isProd) {
    const {createServer: createViteServer} = await import('vite');
    const vite = await createViteServer({
      server: {middlewareMode: true},
      appType: 'spa',
    });
    app.use(vite.middlewares);
  } else {
    const distDir = path.resolve(__dirname, 'dist');
    app.use(express.static(distDir));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distDir, 'index.html'));
    });
  }

  app.listen(port, '0.0.0.0', () => {
    console.log(`JARVIS Workspace Console listening on http://0.0.0.0:${port}`);
  });
}

createServer();
