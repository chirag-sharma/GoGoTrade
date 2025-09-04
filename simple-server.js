// Simple Express server to serve React app
const express = require('express');
const path = require('path');
const app = express();

// Serve static files from the build directory
app.use(express.static(path.join(__dirname, 'frontend/build')));

// Handle React Router - serve index.html for all routes except API
app.get('/', function (req, res) {
  res.sendFile(path.join(__dirname, 'frontend/build', 'index.html'));
});

app.get('/about', function (req, res) {
  res.sendFile(path.join(__dirname, 'frontend/build', 'index.html'));
});

// Catch all other routes and send index.html
app.use('*', function (req, res) {
  res.sendFile(path.join(__dirname, 'frontend/build', 'index.html'));
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`🚀 GoGoTrade Frontend serving on http://localhost:${port}`);
  console.log(`📂 Serving from: ${path.join(__dirname, 'frontend/build')}`);
  console.log(`⏰ Started at: ${new Date()}`);
});
