const http = require('http');
const os = require('os');

const PORT = process.env.PORT || 8080;
const SERVICE_NAME = process.env.SERVICE_NAME || 'node-api';
const DB_HOST = process.env.DB_HOST || 'database';

const response = {
    message: '',
    service: SERVICE_NAME,
    language: 'Node.js',
    version: '20',
    db_host: DB_HOST,
    platform: os.platform(),
    arch: os.arch()
};

const server = http.createServer((req, res) => {
    res.setHeader('Content-Type', 'application/json');
    
    if (req.url === '/health') {
        response.message = 'OK';
        res.writeHead(200);
        res.end(JSON.stringify(response, null, 2));
    } else if (req.url === '/api') {
        response.message = 'Hello from Node.js service!';
        res.writeHead(200);
        res.end(JSON.stringify(response, null, 2));
    } else {
        res.writeHead(404);
        res.end(JSON.stringify({ error: 'Not found' }));
    }
});

server.listen(PORT, () => {
    console.log(`Node.js service listening on port ${PORT}`);
});
