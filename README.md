# Fantasy Life

Fantasy Life es una **webapp de juego social** (romántica y sugerente, pero elegante) donde dos personas —o una red de usuarios— se retan a **cumplir deseos** dentro de periodos de tiempo definidos.  
Incluye negociación de fechas, sorpresa, puntuaciones, rankings y control total de privacidad.

Este repositorio define la **base técnica y funcional** del proyecto y sirve como **documentación de referencia** antes de la implementación completa.

---

## 🧠 Concepto del juego

- Cada usuario crea una **lista de deseos** personalizados.
- Los deseos se agrupan en **categorías globales** (ej. Deseo, Fantasía, Plan).
- Cada categoría tiene **reglas propias** (límites y tiempos).
- Cada periodo (por defecto mensual), el sistema asigna **aleatoriamente** un deseo del otro jugador.
- El jugador que debe cumplir el deseo **negocia fecha y hora** con el creador.
- Una vez cumplido, se marca como **ejecutado**, se **puntúa**, se comenta y cuenta para rankings.

El valor diferencial es la **sorpresa**:  
el deseo se conoce, pero el *cuándo* no.

---

## 🎮 Modos de juego

### 🔒 Modo privado (pareja)
- Emparejamiento por aceptación mutua.
- No se pueden rechazar deseos.
- Reglas de categorías y tiempos **pactadas entre ambos**.
- Ideal para parejas.

### 🌐 Modo público (red)
- Interacción con otros usuarios.
- Los deseos pueden **rechazarse sin penalización**.
- Reglas globales fijas.
- El usuario puede **desactivarse de la red pública por periodos**.

---

## 👶 Menores y restricciones

- Registro con **fecha de nacimiento** (autodeclaración).
- Usuarios menores de edad:
  - No ven ni pueden seleccionar categorías marcadas como adultas.
  - No reciben contenido adulto por API ni WebSocket.
- Las restricciones se aplican **en backend**, no solo en frontend.

---

## 🔐 Privacidad

- **Nickname obligatorio**
- **Foto opcional**
- **Datos reales opcionales** (nombre, bio, etc.)
- Control fino de privacidad:
  - El usuario decide **a qué otros usuarios** mostrar datos reales.
- El perfil público muestra **solo lo permitido**.

---

## 🏆 Rankings

Rankings globales automáticos:
- Más deseos cumplidos
- Mejor puntuación media
- Menor tiempo medio de cumplimiento

Los rankings se calculan solo con deseos **ejecutados y valorados**.

---

## 🧱 Arquitectura técnica

### Stack

**Frontend**
- React
- Vite
- JavaScript (NO TypeScript)
- React Router
- Axios
- WebSocket nativo

**Backend**
- Django 5
- Django REST Framework
- Django Channels (WebSockets)
- Redis (Channels layer)

**Base de datos**
- SQLite (desarrollo)
- PostgreSQL (producción / futuro)

**Infraestructura**
- Docker
- Docker Compose
- (Opcional) Nginx en producción

---

## 🗂️ Estructura del repositorio

```
/
├─ apps/
│  ├─ api/        # Backend Django
│  └─ web/        # Frontend React + Vite
├─ infra/         # Docker, nginx, scripts
├─ docker-compose.yml
└─ README.md
```

---

## 🐳 Docker (obligatorio)

Todo el proyecto está pensado para ejecutarse **exclusivamente con Docker**.

Servicios:
- `api` → Django + DRF + Channels
- `web` → React + Vite
- `redis` → WebSockets
- `postgres` → preparado para producción (opcional en dev)

### Arranque en desarrollo

```bash
docker compose up --build
```

URLs:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000

---

## 🗄️ Base de datos

### Desarrollo (por defecto)
- SQLite (`db.sqlite3`)

### Producción (futuro)
- PostgreSQL

El cambio se hace **solo por variables de entorno**, sin tocar código.

---

## 🔑 Autenticación y seguridad

- Usuario custom con email como identificador
- Password hashing con **Argon2**
- JWT con refresh tokens
- Rate limit en login y registro
- Permisos estrictos por match
- Protección contra acceso a recursos ajenos

---

## 📌 Estado

🟡 Diseño y especificación cerrados  
🔜 Implementación mediante prompt controlado

---

© 2025 — Fantasy Life