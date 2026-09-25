const http = require('http');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

const ROOT = __dirname;
const WEB_ROOT = path.join(ROOT, 'web');
const PYTHON_PORT = 8765;
const NODE_PORT = Number(process.env.PORT || 3000);
const pythonExecutable = path.join(ROOT, 'jarvis', '.venv', 'Scripts', 'python.exe');
const python = spawn(fs.existsSync(pythonExecutable) ? pythonExecutable : 'python', ['main.py'], {
  cwd: ROOT,
  env: { ...process.env, PYTHONUNBUFFERED: '1' },
  stdio: 'inherit'
});

python.on('error', (error) => console.error(`Could not start Python backend: ${error.message}`));
python.on('exit', (code) => {
  if (code !== 0 && code !== null) console.error(`Python backend exited with code ${code}`);
});

const contentTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.png': 'image/png',
  '.gif': 'image/gif',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp'
};

function serveStatic(request, response) {
  const requested = request.url === '/' ? '/index.html' : request.url.split('?')[0];
  const filePath = path.resolve(WEB_ROOT, `.${requested}`);
  if (!filePath.startsWith(WEB_ROOT) || !fs.existsSync(filePath)) {
    response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
    response.end('Not found');
    return;
  }
  response.writeHead(200, { 'Content-Type': contentTypes[path.extname(filePath).toLowerCase()] || 'application/octet-stream' });
  fs.createReadStream(filePath).pipe(response);
}

function proxyToPython(request, response) {
  const proxyRequest = http.request({
    hostname: '127.0.0.1',
    port: PYTHON_PORT,
    path: request.url,
    method: request.method,
    headers: { ...request.headers, host: `127.0.0.1:${PYTHON_PORT}` }
  }, (proxyResponse) => {
    response.writeHead(proxyResponse.statusCode, proxyResponse.headers);
    proxyResponse.pipe(response);
  });
  proxyRequest.on('error', () => {
    response.writeHead(503, { 'Content-Type': 'application/json' });
    response.end(JSON.stringify({ error: 'Jarvis Python backend is starting or unavailable' }));
  });
  request.pipe(proxyRequest);
}

const server = http.createServer((request, response) => {
  if (request.url.startsWith('/api/')) proxyToPython(request, response);
  else serveStatic(request, response);
});

server.listen(NODE_PORT, '0.0.0.0', () => {
  console.log(`Jarvis Node.js UI: http://localhost:${NODE_PORT}`);
  console.log(`Phone URL: http://YOUR-PC-IP:${NODE_PORT}`);
});

function shutdown() {
  python.kill();
  server.close(() => process.exit(0));
}
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);
