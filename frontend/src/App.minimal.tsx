/**
 * Minimal App Component - Just React, no MUI or Redux
 */

import React from 'react';

function App() {
  return (
    <div style={{ 
      padding: '20px', 
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#121212',
      color: 'white',
      minHeight: '100vh'
    }}>
      <h1>🚀 GoGoTrade - Minimal Version</h1>
      <p>Frontend is running successfully!</p>
      <p>Backend API Status: <span id="api-status">Checking...</span></p>
      
      <script>{`
        fetch('http://localhost:8000/api/v1/status')
          .then(response => response.json())
          .then(data => {
            document.getElementById('api-status').textContent = data.message || 'Connected';
          })
          .catch(error => {
            document.getElementById('api-status').textContent = 'Backend not connected';
          });
      `}</script>
    </div>
  );
}

export default App;
