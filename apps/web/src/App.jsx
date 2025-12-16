import { useState, useEffect } from 'react'
import './App.css'
import api from './api'

function App() {
  const [status, setStatus] = useState('Checking API connection...')
  const [categories, setCategories] = useState([])
  const [wishes, setWishes] = useState([])
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [user, setUser] = useState(null)

  useEffect(() => {
    checkAuth()
    checkAPI()
  }, [])

  const checkAuth = () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      setIsLoggedIn(true)
      fetchUser()
    }
  }

  const checkAPI = async () => {
    try {
      const response = await api.get('/api/')
      setStatus('✅ API Connected')
      if (isLoggedIn) {
        fetchCategories()
        fetchWishes()
      }
    } catch (error) {
      setStatus('⚠️ API connection failed')
      console.error('API Error:', error)
    }
  }

  const fetchUser = async () => {
    try {
      const response = await api.get('/api/users/me/')
      setUser(response.data)
    } catch (error) {
      console.error('Failed to fetch user:', error)
      setIsLoggedIn(false)
    }
  }

  const fetchCategories = async () => {
    try {
      const response = await api.get('/api/categories/')
      setCategories(response.data)
    } catch (error) {
      console.error('Failed to fetch categories:', error)
    }
  }

  const fetchWishes = async () => {
    try {
      const response = await api.get('/api/wishes/')
      setWishes(response.data)
    } catch (error) {
      console.error('Failed to fetch wishes:', error)
    }
  }

  return (
    <div className="App">
      <header>
        <h1>🎮 Fantasy Life</h1>
        <p className="tagline">
          Una webapp de juego social para cumplir deseos
        </p>
        {user && (
          <div className="user-info">
            <p>Bienvenido, <strong>{user.nickname}</strong></p>
          </div>
        )}
      </header>
      
      <main>
        <div className="status-card">
          <h2>Estado del Sistema</h2>
          <p>{status}</p>
        </div>

        {isLoggedIn ? (
          <>
            <div className="info-card">
              <h3>📋 Categorías Disponibles</h3>
              {categories.length > 0 ? (
                <div className="categories-list">
                  {categories.map(cat => (
                    <div key={cat.id} className="category-item">
                      <strong>{cat.name}</strong> {cat.is_adult ? '🔞' : ''}
                      <p>{cat.description}</p>
                      <small>
                        Máx. {cat.max_wishes_per_period} deseo(s) por periodo • 
                        {cat.min_days_to_complete}-{cat.max_days_to_complete} días
                      </small>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No hay categorías disponibles</p>
              )}
            </div>

            <div className="info-card">
              <h3>💭 Mis Deseos</h3>
              {wishes.length > 0 ? (
                <div className="wishes-list">
                  {wishes.map(wish => (
                    <div key={wish.id} className="wish-item">
                      <strong>{wish.title}</strong>
                      <p>{wish.description}</p>
                      <small>
                        Categoría: {wish.category_name} •
                        {wish.is_active ? ' ✅ Activo' : ' ❌ Inactivo'}
                      </small>
                    </div>
                  ))}
                </div>
              ) : (
                <p>No has creado deseos todavía</p>
              )}
            </div>
          </>
        ) : (
          <div className="info-card">
            <h3>🔐 Inicia Sesión</h3>
            <p>Para acceder a todas las funcionalidades, necesitas iniciar sesión.</p>
            <p>Usa el API endpoint <code>/api/token/</code> para obtener tu token JWT.</p>
          </div>
        )}
        
        <div className="info-card">
          <h3>🎯 Funcionalidades</h3>
          <div className="features-grid">
            <div className="feature">
              <h4>✨ Deseos Personalizados</h4>
              <p>Crea listas de deseos en diferentes categorías</p>
            </div>
            <div className="feature">
              <h4>🎲 Asignación Aleatoria</h4>
              <p>El sistema asigna deseos sorpresa cada periodo</p>
            </div>
            <div className="feature">
              <h4>📅 Negociación de Fechas</h4>
              <p>Acuerda cuándo cumplir cada deseo</p>
            </div>
            <div className="feature">
              <h4>⭐ Puntuación y Rankings</h4>
              <p>Valora y compite en rankings globales</p>
            </div>
            <div className="feature">
              <h4>🔒 Modo Privado</h4>
              <p>Para parejas con reglas personalizadas</p>
            </div>
            <div className="feature">
              <h4>🌐 Modo Público</h4>
              <p>Red social con libertad de rechazo</p>
            </div>
          </div>
        </div>

        <div className="info-card">
          <h3>🛠️ Stack Tecnológico</h3>
          <div className="stack-info">
            <div>
              <strong>Frontend:</strong>
              <ul>
                <li>React</li>
                <li>Vite</li>
                <li>React Router</li>
                <li>Axios</li>
                <li>WebSocket nativo</li>
              </ul>
            </div>
            <div>
              <strong>Backend:</strong>
              <ul>
                <li>Django 5.1.15</li>
                <li>Django REST Framework</li>
                <li>Django Channels</li>
                <li>JWT Authentication</li>
                <li>Argon2 Password Hashing</li>
              </ul>
            </div>
          </div>
        </div>

        <div className="info-card">
          <h3>📊 API Endpoints</h3>
          <ul className="endpoints-list">
            <li><code>POST /api/users/</code> - Registro</li>
            <li><code>POST /api/token/</code> - Login (JWT)</li>
            <li><code>GET /api/categories/</code> - Listar categorías</li>
            <li><code>GET /api/wishes/</code> - Listar deseos</li>
            <li><code>GET /api/matches/</code> - Ver matches</li>
            <li><code>GET /api/assignments/</code> - Ver asignaciones</li>
            <li><code>GET /api/rankings/most_completed/</code> - Rankings</li>
          </ul>
        </div>
      </main>
      
      <footer>
        <p>© 2025 — Fantasy Life</p>
        <p><small>Ejecutable con Docker: <code>docker compose up --build</code></small></p>
      </footer>
    </div>
  )
}

export default App
