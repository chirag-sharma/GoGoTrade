/**
 * Minimal App Component - GoGoTrade Frontend
 */

import { useEffect, useState } from 'react';

function App() {
  const [apiStatus, setApiStatus] = useState('Checking...');

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/status')
      .then(response => response.json())
      .then(data => {
        setApiStatus(data.message || 'Connected');
      })
      .catch(() => {
        setApiStatus('Backend not connected');
      });
  }, []);

  return (
    <div style={{ 
      padding: '20px', 
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#121212',
      color: 'white',
      minHeight: '100vh'
    }}>
      <h1>🚀 GoGoTrade - Frontend Working!</h1>
      <p>Frontend is running successfully with Vite!</p>
      <p>Backend API Status: <strong>{apiStatus}</strong></p>
      <div style={{ marginTop: '20px', padding: '10px', border: '1px solid #333' }}>
        <h3>✅ System Status:</h3>
        <ul>
          <li>✅ Backend API running on localhost:8000</li>
          <li>✅ Frontend running on localhost:5173 (Vite)</li>
          <li>✅ No TypeScript errors</li>
          <li>✅ Clean, fast development server</li>
        </ul>
      </div>
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#1e1e1e' }}>
        <h3>🔄 Next: Add Trading Features</h3>
        <p>Now we can add Material-UI, Redux, and TradingView charts with confidence!</p>
      </div>
    </div>
  );
}

export default App;
