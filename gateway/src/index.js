/**
 * API Gateway & WebSocket Server for AI Research Multi-Agent System.
 *
 * - Proxies REST requests to the Django backend
 * - Provides WebSocket connections for real-time research status updates
 * - Subscribes to Redis pub/sub for pipeline phase change notifications
 * - JWT authentication for both HTTP and WebSocket connections
 * - Rate limiting, CORS, compression, security headers
 */

const express = require('express');
const http = require('http');
const { WebSocketServer } = require('ws');
const { createProxyMiddleware } = require('http-proxy-middleware');
const Redis = require('ioredis');
const jwt = require('jsonwebtoken');
const cors = require('cors');
const morgan = require('morgan');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const compression = require('compression');
const url = require('url');

// Configuration
const PORT = process.env.PORT || 3046;
const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:8000';
const REDIS_URL = process.env.REDIS_URL || 'redis://redis:6379/0';
const JWT_SECRET = process.env.JWT_SECRET || 'change-this-jwt-secret';

const app = express();
const server = http.createServer(app);

// ── Middleware ──────────────────────────────────────────────────────────────

app.use(helmet({ contentSecurityPolicy: false }));
app.use(compression());
app.use(cors({
  origin: ['http://localhost:3045', 'http://localhost:3046'],
  credentials: true,
}));
app.use(morgan('short'));

// Rate limiting
const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
});
app.use('/api/', limiter);

// Health check
app.get('/health', (_req, res) => {
  res.json({ status: 'ok', service: 'ai-research-gateway', timestamp: new Date().toISOString() });
});

// ── API Proxy to Django Backend ─────────────────────────────────────────────

app.use('/api', createProxyMiddleware({
  target: BACKEND_URL,
  changeOrigin: true,
  pathRewrite: { '^/': '/api/' },
  timeout: 300000,
  proxyTimeout: 300000,
  onError: (err, _req, res) => {
    console.error('Proxy error:', err.message);
    res.status(502).json({ error: 'Backend service unavailable' });
  },
}));

// ── WebSocket Server ────────────────────────────────────────────────────────

const wss = new WebSocketServer({ noServer: true });

// Map: userId -> Set<WebSocket>
const clientsByUser = new Map();
// Map: sessionId -> Set<WebSocket>
const clientsBySession = new Map();

/**
 * Authenticate WebSocket connection via JWT token in query string.
 */
function authenticateWS(request) {
  try {
    const { query } = url.parse(request.url, true);
    const token = query.token;
    if (!token) return null;
    const decoded = jwt.verify(token, JWT_SECRET);
    return decoded;
  } catch (err) {
    return null;
  }
}

server.on('upgrade', (request, socket, head) => {
  const user = authenticateWS(request);
  if (!user) {
    socket.write('HTTP/1.1 401 Unauthorized\r\n\r\n');
    socket.destroy();
    return;
  }

  wss.handleUpgrade(request, socket, head, (ws) => {
    ws.user = user;
    wss.emit('connection', ws, request);
  });
});

wss.on('connection', (ws, request) => {
  const userId = ws.user.user_id;
  console.log(`WebSocket connected: user=${userId}`);

  // Track user connection
  if (!clientsByUser.has(userId)) {
    clientsByUser.set(userId, new Set());
  }
  clientsByUser.get(userId).add(ws);

  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data);

      // Subscribe to session updates
      if (msg.type === 'subscribe_session') {
        const sessionId = msg.session_id;
        if (!clientsBySession.has(sessionId)) {
          clientsBySession.set(sessionId, new Set());
        }
        clientsBySession.get(sessionId).add(ws);
        ws.subscribedSessions = ws.subscribedSessions || new Set();
        ws.subscribedSessions.add(sessionId);

        ws.send(JSON.stringify({
          type: 'subscribed',
          session_id: sessionId,
        }));
      }

      // Unsubscribe from session
      if (msg.type === 'unsubscribe_session') {
        const sessionId = msg.session_id;
        if (clientsBySession.has(sessionId)) {
          clientsBySession.get(sessionId).delete(ws);
        }
        if (ws.subscribedSessions) {
          ws.subscribedSessions.delete(sessionId);
        }
      }
    } catch (err) {
      console.error('WebSocket message error:', err.message);
    }
  });

  ws.on('close', () => {
    console.log(`WebSocket disconnected: user=${userId}`);
    if (clientsByUser.has(userId)) {
      clientsByUser.get(userId).delete(ws);
      if (clientsByUser.get(userId).size === 0) {
        clientsByUser.delete(userId);
      }
    }

    // Clean up session subscriptions
    if (ws.subscribedSessions) {
      for (const sessionId of ws.subscribedSessions) {
        if (clientsBySession.has(sessionId)) {
          clientsBySession.get(sessionId).delete(ws);
          if (clientsBySession.get(sessionId).size === 0) {
            clientsBySession.delete(sessionId);
          }
        }
      }
    }
  });

  ws.on('error', (err) => {
    console.error('WebSocket error:', err.message);
  });

  // Send connection confirmation
  ws.send(JSON.stringify({
    type: 'connected',
    message: 'Connected to AI Research Gateway',
    user_id: userId,
  }));
});

// ── Redis Pub/Sub for real-time updates ─────────────────────────────────────

let redisSubscriber;

function setupRedis() {
  try {
    redisSubscriber = new Redis(REDIS_URL);

    redisSubscriber.subscribe('research_updates', (err) => {
      if (err) {
        console.error('Redis subscribe error:', err.message);
        return;
      }
      console.log('Subscribed to research_updates channel');
    });

    redisSubscriber.on('message', (_channel, message) => {
      try {
        const update = JSON.parse(message);
        const sessionId = update.session_id;

        // Broadcast to all clients subscribed to this session
        if (sessionId && clientsBySession.has(sessionId)) {
          const payload = JSON.stringify({
            type: 'session_update',
            ...update,
          });

          for (const ws of clientsBySession.get(sessionId)) {
            if (ws.readyState === 1) { // WebSocket.OPEN
              ws.send(payload);
            }
          }
        }
      } catch (err) {
        console.error('Redis message processing error:', err.message);
      }
    });

    redisSubscriber.on('error', (err) => {
      console.error('Redis error:', err.message);
    });

    console.log('Redis pub/sub connected');
  } catch (err) {
    console.error('Redis connection failed:', err.message);
    console.log('WebSocket will work without real-time Redis updates');
  }
}

// ── Start Server ────────────────────────────────────────────────────────────

server.listen(PORT, () => {
  console.log(`\n🚀 AI Research Gateway running on port ${PORT}`);
  console.log(`   REST proxy → ${BACKEND_URL}`);
  console.log(`   WebSocket → ws://localhost:${PORT}`);
  console.log(`   Health → http://localhost:${PORT}/health\n`);
  setupRedis();
});
