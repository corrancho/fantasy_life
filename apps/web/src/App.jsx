import { useState, useEffect } from 'react'
import './App.css'
import api from './api'

function App() {
  const [status, setStatus] = useState('Checking API connection...')

  useEffect(() => {
    // Test API connection
    const checkAPI = async () => {
      try {
        const response = await api.get('/api/')
        setStatus('✅ API Connected! Backend is ready.')
      } catch (error) {
        setStatus('⚠️ API connection failed. Make sure the backend is running.')
        console.error('API Error:', error)
      }
    }
    
    checkAPI()
  }, [])

  return (
    <div className="App">
      <header>
        <h1>🎮 Fantasy Life</h1>
        <p className="tagline">
          Una webapp de juego social para cumplir deseos
        </p>
      </header>
      
      <main>
        <div className="status-card">
          <h2>Estado del Sistema</h2>
          <p>{status}</p>
        </div>
        
        <div className="info-card">
          <h3>Stack Tecnológico</h3>
          <div className="stack-info">
            <div>
              <strong>Frontend:</strong>
              <ul>
                <li>React</li>
                <li>Vite</li>
                <li>React Router</li>
                <li>Axios</li>
              </ul>
            </div>
            <div>
              <strong>Backend:</strong>
              <ul>
                <li>Django 5</li>
                <li>Django REST Framework</li>
                <li>Django Channels</li>
                <li>JWT Authentication</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
      
      <footer>
        <p>© 2025 — Fantasy Life</p>
      </footer>
    </div>
  )
}

export default App
