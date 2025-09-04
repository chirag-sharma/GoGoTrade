// Simple Express server to serve React app
const express = require('express');
const path = require('path');
const app = express();

console.log('🔄 Starting GoGoTrade Express Server...');

// Enable CORS for API calls
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  next();
});

// Serve static files from the build directory
const buildPath = path.join(__dirname, 'frontend/build');
console.log(`📂 Serving static files from: ${buildPath}`);
app.use(express.static(buildPath));

// Root route
app.get('/', function (req, res) {
  console.log('📥 Serving index.html for route:', req.path);
  res.sendFile(path.join(buildPath, 'index.html'));
});

// Handle any other routes by sending index.html (React Router will handle it)
app.use((req, res) => {
  console.log('📥 Catch-all serving index.html for route:', req.path);
  res.sendFile(path.join(buildPath, 'index.html'));
});

const port = process.env.PORT || 3000;
app.listen(port, '0.0.0.0', () => {
  console.log(`🚀 GoGoTrade Frontend serving on http://localhost:${port}`);
  console.log(`📂 Build directory: ${buildPath}`);
  console.log(`⏰ Server started at: ${new Date()}`);
  console.log(`💡 Access your app at: http://localhost:${port}`);
});
