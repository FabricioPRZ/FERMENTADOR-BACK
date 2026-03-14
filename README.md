# 🧪 Fermentador Backend

API REST para el monitoreo en tiempo real de procesos de fermentación con circuitos ESP32.

![FastAPI](https://img.shields.io/badge/FastAPI-0.135-009688?style=flat&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3-FF6600?style=flat&logo=rabbitmq)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)

---

## 📋 Tabla de contenidos

- [Descripción](#-descripción)
- [Stack tecnológico](#-stack-tecnológico)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Instalación y ejecución](#-instalación-y-ejecución)
- [Variables de entorno](#-variables-de-entorno)
- [Autenticación](#-autenticación)
- [Endpoints](#-endpoints)
  - [Auth](#auth---apiauth)
  - [Users](#users---apiusers)
  - [Circuits](#circuits---apicircuits)
  - [Sensors](#sensors---apisensors)
  - [Fermentation](#fermentation---apifermentation)
  - [Notifications](#notifications---apinotifications)
  - [Formula](#formula---apiformula)
  - [WebSockets](#websockets)
  - [Health](#health)
- [Flujo MQTT / ESP32](#-flujo-mqtt--esp32)
- [Roles y permisos](#-roles-y-permisos)
- [Códigos de error](#-códigos-de-error)

---

## 📖 Descripción

Backend para un sistema de fermentación controlada. Recibe lecturas de sensores desde dispositivos ESP32 vía MQTT/RabbitMQ, las persiste en MySQL, las transmite en tiempo real al frontend vía WebSocket y genera reportes de eficiencia al finalizar cada sesión.

---

## 🛠 Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Framework | FastAPI (async) |
| Base de datos | MySQL 8.0 + SQLAlchemy 2.0 (async) |
| Message broker | RabbitMQ + MQTT (aio-pika) |
| Tiempo real | WebSocket nativo FastAPI |
| Autenticación | JWT (python-jose) + bcrypt |
| Contenedores | Docker Compose |

---

## 🗂 Estructura del proyecto

```
.
├── main.py
├── core/
│   ├── config.py                  # Configuración y variables de entorno
│   ├── database.py                # Motor SQLAlchemy async
│   ├── dependencies.py            # Guards de autenticación y roles
│   ├── security.py                # JWT y bcrypt
│   ├── exceptions.py              # Excepciones HTTP personalizadas
│   ├── rabbitmq/
│   │   ├── connection.py          # Conexión RabbitMQ
│   │   ├── exchanges.py           # Declaración de exchanges y queues
│   │   ├── consumer.py            # Consumidor AMQP + MQTT
│   │   └── publisher.py          # Publicador de comandos al ESP32
│   ├── threads/
│   │   ├── base_sensor_thread.py  # Clase base de hilo por sensor
│   │   └── sensor_thread_manager.py # Gestor de hilos activos
│   └── websocket/
│       ├── websocket_manager.py   # Manager de conexiones WS
│       └── schemas.py             # Schemas de mensajes WS
└── modules/
    ├── auth/
    ├── users/
    ├── circuits/
    ├── sensors/
    ├── fermentation/
    ├── notifications/
    └── formula/
```

Cada módulo sigue arquitectura limpia:

```
module/
├── domain/
│   ├── entities/entities.py       # Dataclasses de dominio
│   ├── dto/schemas.py             # Schemas Pydantic (request/response)
│   └── repository.py             # Interfaz abstracta del repositorio
├── application/
│   └── usecase/                   # Un archivo por caso de uso
└── infrastructure/
    ├── adapters/MySQL.py          # Implementación ORM + repositorio
    ├── controllers/               # Orquestación controller → use case
    └── routes/                    # Router FastAPI (HTTP + WS)
```

---

## 🚀 Instalación y ejecución

### Con Docker (recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/FabricioPRZ/FERMENTADOR-BACK.git
cd sensor-db-backend

# 2. Crear el archivo de entorno
cp .env.example .env
# Editar .env con tus valores

# 3. Levantar los servicios
docker compose up --build
```

La API queda disponible en `http://localhost:8000`
Adminer (gestor de BD) en `http://localhost:8080`

### Sin Docker

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

> Requiere MySQL y RabbitMQ corriendo localmente.

---

## ⚙️ Variables de entorno

```env
# App
APP_NAME=sensor_db_backend
APP_ENV=development
SECRET_KEY=<clave-secreta-jwt>
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# MySQL
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=<contraseña>
DB_NAME=sensor_db

# RabbitMQ
RABBITMQ_HOST=<host>
RABBITMQ_PORT=5672
RABBITMQ_USER=<usuario>
RABBITMQ_PASSWORD=<contraseña>
```

---

## 🔐 Autenticación

Los endpoints protegidos requieren el header:

```
Authorization: Bearer <access_token>
```

El `access_token` se obtiene en `POST /api/auth/login`. Expira según `ACCESS_TOKEN_EXPIRE_MINUTES`. Usa `POST /api/auth/refresh` con el `refresh_token` para renovarlo sin volver a loguearte.

---

## 📡 Endpoints

### Auth — `/api/auth`

#### `POST /api/auth/register`
Registra un nuevo administrador. No requiere autenticación.

**Body:**
```json
{
  "name": "Juan",
  "last_name": "Pérez",
  "email": "juan@email.com",
  "password": "mi-contraseña"
}
```

**Respuesta `201`:**
```json
{
  "id": 1,
  "name": "Juan",
  "last_name": "Pérez",
  "email": "juan@email.com",
  "role": "admin"
}
```

---

#### `POST /api/auth/login`
Autentica al usuario y retorna los tokens.

**Body:**
```json
{
  "email": "juan@email.com",
  "password": "mi-contraseña"
}
```

**Respuesta `200`:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Juan",
    "last_name": "Pérez",
    "email": "juan@email.com",
    "role": "admin"
  }
}
```

---

#### `POST /api/auth/refresh`
Renueva el access token usando el refresh token.

**Body:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Respuesta `200`:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

---

### Users — `/api/users`

> 🔒 Todos los endpoints requieren autenticación.

| Método | Ruta | Descripción | Rol mínimo |
|--------|------|-------------|------------|
| `GET` | `/api/users/` | Listar todos los usuarios | profesor |
| `GET` | `/api/users/{user_id}` | Obtener usuario por ID | profesor |
| `POST` | `/api/users/` | Crear usuario | admin |
| `PUT` | `/api/users/{user_id}` | Actualizar usuario | admin |
| `DELETE` | `/api/users/{user_id}` | Eliminar usuario | admin |

#### `POST /api/users/`

**Body:**
```json
{
  "name": "María",
  "last_name": "García",
  "email": "maria@email.com",
  "password": "contraseña",
  "role": "estudiante",
  "circuit_id": 1
}
```

> `role` acepta: `"admin"`, `"profesor"`, `"estudiante"`

#### `PUT /api/users/{user_id}`
Todos los campos son opcionales.

**Body:**
```json
{
  "name": "María",
  "last_name": "García",
  "email": "nuevo@email.com",
  "password": "nueva-contraseña",
  "role": "profesor"
}
```

---

### Circuits — `/api/circuits`

> 🔒 Activar y consultar requieren autenticación. Crear no requiere (uso interno).

| Método | Ruta | Descripción | Rol mínimo |
|--------|------|-------------|------------|
| `POST` | `/api/circuits/` | Crear nuevo circuito | — |
| `POST` | `/api/circuits/activate` | Activar circuito con código | cualquier rol |
| `GET` | `/api/circuits/me` | Ver mi circuito | cualquier rol |
| `GET` | `/api/circuits/{circuit_id}` | Ver circuito por ID | profesor |

> ⚠️ Los circuitos no activados se eliminan automáticamente después de **30 días** mediante un background task que se ejecuta cada hora.

#### `POST /api/circuits/`
Genera un circuito con código de activación único de 8 caracteres.

**Respuesta `201`:**
```json
{
  "id": 1,
  "activation_code": "A3F9B2C1",
  "created_at": "2025-01-01T00:00:00"
}
```

#### `POST /api/circuits/activate`

**Body:**
```json
{
  "activation_code": "A3F9B2C1"
}
```

**Respuesta `200`:**
```json
{
  "id": 1,
  "activation_code": "A3F9B2C1",
  "is_active": true,
  "motor_on": false,
  "pump_on": false,
  "sensor_alcohol_on": false,
  "sensor_density_on": false,
  "sensor_conductivity_on": false,
  "sensor_ph_on": false,
  "sensor_temperature_on": true,
  "sensor_turbidity_on": false,
  "sensor_rpm_on": true,
  "user_id": 1,
  "activated_at": "2025-01-01T00:00:00",
  "created_at": "2025-01-01T00:00:00",
  "active_sensors": ["temperature", "rpm"]
}
```

---

### Sensors — `/api/sensors`

> 🔒 Requieren autenticación (cualquier rol).

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/sensors/{circuit_id}/{sensor_type}/history` | Historial de lecturas |
| `GET` | `/api/sensors/{circuit_id}/{sensor_type}/latest` | Última lectura |

**Tipos de sensor válidos:** `alcohol` · `density` · `conductivity` · `ph` · `temperature` · `turbidity` · `rpm`

#### `GET /api/sensors/{circuit_id}/{sensor_type}/history`

**Query params opcionales:**

| Param | Tipo | Descripción |
|-------|------|-------------|
| `session_id` | integer | Filtrar por sesión de fermentación |
| `from_dt` | datetime (ISO 8601) | Inicio del rango de fechas |
| `to_dt` | datetime (ISO 8601) | Fin del rango de fechas |

**Ejemplo:**
```
GET /api/sensors/1/rpm/history?session_id=3&from_dt=2025-01-01T00:00:00
```

**Respuesta `200`:**
```json
{
  "circuit_id": 1,
  "sensor_type": "rpm",
  "readings": [
    {
      "id": 1,
      "circuit_id": 1,
      "sensor_type": "rpm",
      "value": 1200.5,
      "session_id": 3,
      "timestamp": "2025-01-01T10:00:00"
    }
  ]
}
```

---

### Fermentation — `/api/fermentation`

> 🔒 Schedule/start/stop requieren `admin` o `profesor`. Report e historial requieren cualquier rol.

| Método | Ruta | Descripción | Rol mínimo |
|--------|------|-------------|------------|
| `POST` | `/api/fermentation/schedule` | Programar fermentación | profesor |
| `POST` | `/api/fermentation/{session_id}/start` | Iniciar sesión | profesor |
| `POST` | `/api/fermentation/{session_id}/stop` | Detener sesión | profesor |
| `GET` | `/api/fermentation/{session_id}/report` | Obtener reporte | cualquier rol |
| `GET` | `/api/fermentation/history` | Historial de reportes del usuario | cualquier rol |

#### `POST /api/fermentation/schedule`

**Body:**
```json
{
  "circuit_id": 1,
  "scheduled_start": "2025-06-01T08:00:00",
  "scheduled_end": "2025-06-08T08:00:00",
  "initial_sugar": 120.5
}
```

**Respuesta `201`:**
```json
{
  "id": 1,
  "circuit_id": 1,
  "user_id": 1,
  "formula_id": 1,
  "scheduled_start": "2025-06-01T08:00:00",
  "scheduled_end": "2025-06-08T08:00:00",
  "actual_start": null,
  "actual_end": null,
  "status": "scheduled",
  "interrupted_by": null,
  "created_at": "2025-05-30T10:00:00"
}
```

#### `POST /api/fermentation/{session_id}/start`
No requiere body. Cambia el estado a `running`, registra los valores iniciales de los sensores activos y lanza un hilo de escucha por cada sensor.

#### `POST /api/fermentation/{session_id}/stop`

**Body:**
```json
{
  "interrupted": false
}
```

> `interrupted: true` marca la sesión como `"interrupted"`. `false` o ausente la marca como `"completed"`.

#### `GET /api/fermentation/{session_id}/report`

**Respuesta `200` (ejemplo parcial):**
```json
{
  "id": 1,
  "session_id": 1,
  "initial_sugar": 120.5,
  "final_sugar": null,
  "ethanol_detected": 58.3,
  "theoretical_ethanol": 61.45,
  "efficiency": 94.87,
  "temperature_initial": 20.1,
  "temperature_final": 22.4,
  "temperature_deactivated_at": null,
  "temperature_last_reading": null,
  "rpm_initial": 1200.0,
  "rpm_final": 1180.5,
  "rpm_deactivated_at": null,
  "rpm_last_reading": null,
  "notes": null,
  "generated_at": "2025-06-08T08:00:00"
}
```

> El reporte incluye los campos `{sensor}_initial`, `{sensor}_final`, `{sensor}_deactivated_at` y `{sensor}_last_reading` para cada uno de los 7 sensores.

---

### Notifications — `/api/notifications`

> 🔒 Todos requieren autenticación (cualquier rol).

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/notifications/` | Listar notificaciones del usuario |
| `PATCH` | `/api/notifications/{notification_id}/read` | Marcar una como leída |
| `PATCH` | `/api/notifications/read-all` | Marcar todas como leídas |

#### `GET /api/notifications/`

**Query params opcionales:**

| Param | Tipo | Descripción |
|-------|------|-------------|
| `only_unread` | boolean | `true` = solo no leídas. Default: `false` |

**Tipos de notificación posibles:** `high_temperature` · `fermentation_complete` · `fermentation_interrupted` · `sensor_failure` · `general`

---

### Formula — `/api/formula`

> 🔒 Lectura requiere cualquier rol. Editar y activar requieren `admin` o `profesor`.

| Método | Ruta | Descripción | Rol mínimo |
|--------|------|-------------|------------|
| `GET` | `/api/formula/active` | Fórmula activa actual | cualquier rol |
| `GET` | `/api/formula/` | Listar todas las fórmulas | cualquier rol |
| `GET` | `/api/formula/{formula_id}` | Obtener fórmula por ID | cualquier rol |
| `PUT` | `/api/formula/{formula_id}` | Editar fórmula | profesor |
| `PATCH` | `/api/formula/{formula_id}/activate` | Cambiar fórmula activa | profesor |

#### `PUT /api/formula/{formula_id}`
Todos los campos son opcionales.

**Body:**
```json
{
  "name": "Fórmula estándar Gay-Lussac",
  "conversion_factor": 0.51,
  "description": "eficiencia = (etanol_sensor / (azucar_inicial * factor)) * 100"
}
```

> `conversion_factor` debe ser > 0. Solo puede haber una fórmula activa a la vez.

---

### WebSockets

Los WebSockets **no** llevan el prefijo `/api`.

#### `WS /ws/sensors/{circuit_id}`
Canal **Back → Front**. Emite lecturas en tiempo real cada vez que el ESP32 publica datos vía MQTT.

**Mensaje de lectura activa:**
```json
{
  "type": "sensor_data",
  "sensor_type": "rpm",
  "value": 1200.5,
  "circuit_id": 1,
  "session_id": 3,
  "timestamp": "2025-01-01T10:00:00",
  "active": true
}
```

**Mensaje de sensor desactivado:**
```json
{
  "type": "sensor_deactivated",
  "sensor_type": "temperature",
  "circuit_id": 1,
  "session_id": 3,
  "last_reading": 25.4,
  "occurred_at": "2025-01-01T10:30:00"
}
```

---

#### `WS /ws/notifications/{user_id}`
Canal **Back → Front**. Emite alertas en tiempo real.

**Mensaje de notificación:**
```json
{
  "type": "high_temperature",
  "notification_id": 42,
  "message": "⚠️ Temperatura crítica: 41.5°C (umbral: 40°C)",
  "session_id": 3,
  "occurred_at": "2025-01-01T10:00:00"
}
```

---

#### `WS /ws/circuit/{circuit_id}/commands`
Canal **Front → Back → RabbitMQ → ESP32**. El backend actúa como puente, no persiste los comandos.

**Mensaje de comando:**
```json
{
  "command_type": "motor_on",
  "payload": {}
}
```

**Tipos de comando disponibles:**

| Comando | Descripción |
|---------|-------------|
| `sensor_on` / `sensor_off` | Activar / desactivar sensor |
| `motor_on` / `motor_off` | Encender / apagar motor |
| `pump_on` / `pump_off` | Encender / apagar bomba |
| `start_fermentation` / `stop_fermentation` | Iniciar / detener fermentación |

**Respuesta del servidor:**
```json
{
  "status": "ok",
  "command": "motor_on"
}
```

---

### Health

#### `GET /health`
No requiere autenticación.

**Respuesta `200`:**
```json
{
  "status": "ok",
  "database": "connected",
  "rabbitmq": "connected"
}
```

---

## 📡 Flujo MQTT / ESP32

El ESP32 publica lecturas de sensores en los siguientes topics MQTT:

```
sensors/{circuit_id}/{sensor_type}
```

**Ejemplos:**
- `sensors/1/temperature`
- `sensors/1/rpm`
- `sensors/2/ph`

**Payload esperado:**
```json
{
  "value": 1200.5,
  "session_id": 3,
  "active": true
}
```

> `active: false` indica que el sensor fue desactivado. El backend registra la última lectura y notifica al frontend.

El backend publica comandos de vuelta al ESP32 con el routing key:
```
commands.{circuit_id}.{command_type}
```

### Diagrama de flujo

```
ESP32 ──MQTT──► RabbitMQ ──amq.topic──► Backend
                                          │
                                    ┌─────┴─────┐
                                    │           │
                                  MySQL      WebSocket
                                    │           │
                                    └─────┬─────┘
                                        Front
```

---

## 👥 Roles y permisos

| Acción | estudiante | profesor | admin |
|--------|:----------:|:--------:|:-----:|
| Ver sensores e historial | ✅ | ✅ | ✅ |
| Ver reportes | ✅ | ✅ | ✅ |
| Ver notificaciones | ✅ | ✅ | ✅ |
| Ver circuito propio | ✅ | ✅ | ✅ |
| Ver circuitos por ID | ❌ | ✅ | ✅ |
| Programar / iniciar / detener fermentación | ❌ | ✅ | ✅ |
| Editar fórmulas | ❌ | ✅ | ✅ |
| Ver todos los usuarios | ❌ | ✅ | ✅ |
| Crear / editar / eliminar usuarios | ❌ | ✅ | ✅ |

---

## ❌ Códigos de error

| Código | Cuándo ocurre |
|--------|--------------|
| `400 Bad Request` | Datos inválidos, fechas incorrectas o parámetros fuera de rango |
| `401 Unauthorized` | Token ausente, inválido o expirado |
| `403 Forbidden` | El rol del usuario no tiene permiso para la acción |
| `404 Not Found` | El recurso no existe (usuario, circuito, sesión, etc.) |
| `409 Conflict` | Email duplicado, circuito ya activado, fermentación ya en curso |
| `503 Service Unavailable` | Error de conexión con RabbitMQ |

**Formato estándar de respuesta de error:**
```json
{
  "detail": "Descripción del error"
}
```
