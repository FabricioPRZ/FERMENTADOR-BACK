# Fermentador Backend — Documentación de la API

**Versión:** 1.0.0  
**Base URL:** `http://localhost:8000`  
**Descripción:** API para monitoreo de fermentación con sensores ESP32 en tiempo real.

---

## Tabla de contenidos

1. [Arquitectura general](#arquitectura-general)
2. [Autenticación](#autenticación)
3. [Roles y permisos](#roles-y-permisos)
4. [Códigos de error](#códigos-de-error)
5. [Endpoints REST](#endpoints-rest)
   - [Auth](#auth)
   - [Users](#users)
   - [Circuits](#circuits)
   - [Sensors](#sensors)
   - [Fermentation](#fermentation)
   - [Notifications](#notifications)
   - [Formula](#formula)
   - [Health](#health)
6. [WebSockets](#websockets)
   - [WS Sensors](#ws-sensors)
   - [WS Notifications](#ws-notifications)
   - [WS Circuit Commands](#ws-circuit-commands)
7. [Modelos de datos](#modelos-de-datos)
8. [Esquema de base de datos](#esquema-de-base-de-datos)
9. [Configuración e infraestructura](#configuración-e-infraestructura)
10. [Variables de entorno](#variables-de-entorno)

---

## Arquitectura general

El sistema sigue una arquitectura **Clean Architecture / Hexagonal** con las siguientes capas:

```
ESP32 ──MQTT──► RabbitMQ ──AMQP──► Consumer ──► DB (MySQL)
                                       │
                                       └──► WebSocket ──► Frontend
```

- **ESP32** publica lecturas de sensores por MQTT.
- **RabbitMQ** actúa como broker entre ESP32 y el backend.
- **Consumer** procesa mensajes de las queues AMQP y MQTT.
- **WebSocket Manager** emite datos en tiempo real al frontend.
- **Sensor Thread Manager** gestiona hilos dedicados por sensor durante una sesión.

---

## Autenticación

La API usa **JWT Bearer Token**.

Incluir en cada request protegido:

```
Authorization: Bearer <access_token>
```

### Tokens

| Token | Duración (default) | Descripción |
|---|---|---|
| `access_token` | 60 minutos | Para todas las peticiones autenticadas |
| `refresh_token` | 7 días | Para obtener un nuevo `access_token` |

### Payload del JWT

```json
{
  "sub": "1",
  "role": "admin",
  "circuit_id": 3,
  "exp": 1710000000,
  "iat": 1709996400
}
```

---

## Roles y permisos

| Rol | ID | Descripción |
|---|---|---|
| `admin` | 1 | Acceso total. Puede crear profesores y estudiantes |
| `profesor` | 2 | Puede crear estudiantes y ver sus propios usuarios |
| `estudiante` | 3 | Solo puede ver gráficas, historial y reportes |

### Guards disponibles

| Guard | Roles permitidos |
|---|---|
| `require_admin` | admin |
| `require_admin_or_profesor` | admin, profesor |
| `require_any_role` | admin, profesor, estudiante |

---

## Códigos de error

Todos los errores siguen el formato estándar de FastAPI:

```json
{
  "detail": "Mensaje de error descriptivo"
}
```

| Código | Descripción |
|---|---|
| `400` | Solicitud inválida (`BadRequestException`) |
| `401` | No autenticado — credenciales inválidas, token expirado o inválido |
| `403` | Sin permisos para la acción (`ForbiddenException`) |
| `404` | Recurso no encontrado |
| `409` | Conflicto con el estado actual del recurso |
| `503` | Servicio no disponible (broker RabbitMQ) |

### Errores de autenticación

| Error | Código | Mensaje |
|---|---|---|
| `InvalidCredentialsException` | 401 | Credenciales inválidas |
| `TokenExpiredException` | 401 | El token ha expirado |
| `TokenInvalidException` | 401 | Token inválido |
| `UnauthorizedException` | 401 | No autorizado |
| `ForbiddenException` | 403 | No tienes permisos para realizar esta acción |
| `EmailAlreadyExistsException` | 409 | El email ya está registrado |

### Errores de dominio

| Error | Código | Mensaje |
|---|---|---|
| `UserNotFoundException` | 404 | Usuario no encontrado |
| `UserAlreadyExistsException` | 409 | Ya existe un usuario con ese email |
| `CircuitNotFoundException` | 404 | Circuito no encontrado |
| `CircuitAlreadyActivatedException` | 409 | Este código de activación ya fue utilizado |
| `CircuitNotActivatedException` | 400 | El circuito no está activado |
| `InvalidActivationCodeException` | 400 | Código de activación inválido o no existe |
| `ActivationCodeExpiredException` | 400 | El código de activación ha expirado (30 días sin usar) |
| `FermentationSessionNotFoundException` | 404 | Sesión de fermentación no encontrada |
| `FermentationAlreadyRunningException` | 409 | Ya hay una fermentación en curso para este circuito |
| `FermentationNotRunningException` | 400 | No hay una fermentación en curso para este circuito |
| `FermentationReportNotFoundException` | 404 | Reporte de fermentación no encontrado |
| `SensorNotFoundException` | 404 | Sensor `{sensor_type}` no encontrado |
| `SensorDisabledException` | 400 | El sensor `{sensor_type}` está desactivado |
| `FormulaNotFoundException` | 404 | Fórmula de eficiencia no encontrada |
| `BrokerConnectionException` | 503 | No se pudo conectar al broker de mensajería |
| `MessagePublishException` | 503 | Error al publicar mensaje en el broker |

---

## Endpoints REST

### Auth

Prefijo: `/api/auth`

---

#### `POST /api/auth/register`

Registra un nuevo administrador en el sistema.

**Auth requerida:** No

**Request Body:**

```json
{
  "name": "Juan",
  "last_name": "García",
  "email": "juan@ejemplo.com",
  "password": "contraseña123"
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `name` | `string` | ✅ | Nombre del usuario |
| `last_name` | `string` | ✅ | Apellido del usuario |
| `email` | `string (email)` | ✅ | Email único |
| `password` | `string` | ✅ | Contraseña en texto plano (se hashea internamente) |

**Response `201`:**

```json
{
  "id": 1,
  "name": "Juan",
  "last_name": "García",
  "email": "juan@ejemplo.com",
  "role": "admin"
}
```

**Errores:**
- `409` — El email ya está registrado

> **Nota:** El admin se crea sin circuito asignado. El `circuit_id` se obtiene al activar el circuito con `POST /api/users/me/activate`.

---

#### `POST /api/auth/login`

Inicia sesión y obtiene tokens JWT.

**Auth requerida:** No

**Request Body:**

```json
{
  "email": "juan@ejemplo.com",
  "password": "contraseña123"
}
```

**Response `200`:**

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Juan",
    "last_name": "García",
    "email": "juan@ejemplo.com",
    "role": "admin",
    "circuit_id": 3
  }
}
```

**Errores:**
- `401` — Credenciales inválidas

---

#### `POST /api/auth/refresh`

Renueva el `access_token` usando el `refresh_token`.

**Auth requerida:** No

**Request Body:**

```json
{
  "refresh_token": "eyJ..."
}
```

**Response `200`:**

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Errores:**
- `401` — Token inválido o expirado
- `404` — Usuario no encontrado

---

### Users

Prefijo: `/api/users`

---

#### `POST /api/users/me/activate`

Activa el circuito del admin ingresando el código de activación físico del hardware.

**Auth requerida:** `require_any_role`

**Request Body:**

```json
{
  "activation_code": "A1B2C3D4"
}
```

**Response `200`:**

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "circuit_id": 3
}
```

> **Nota:** Devuelve un nuevo `access_token` con el `circuit_id` incluido en el payload. El admin debe reemplazar su token actual con este. La operación es permanente: un usuario solo puede activar un circuito una vez.

**Errores:**
- `400` — Ya tienes un circuito asignado
- `400` — Código de activación inválido o expirado (30 días)
- `404` — Usuario no encontrado

---

#### `GET /api/users/`

Retorna todos los usuarios creados por el usuario autenticado.

**Auth requerida:** `require_admin_or_profesor`

**Response `200`:**

```json
[
  {
    "id": 2,
    "name": "Ana",
    "last_name": "López",
    "email": "ana@ejemplo.com",
    "role_id": 2,
    "role_name": "profesor",
    "circuit_id": 3,
    "created_by": 1,
    "created_at": "2024-01-15T10:00:00"
  }
]
```

---

#### `GET /api/users/{user_id}`

Obtiene un usuario específico por su ID.

**Auth requerida:** `require_admin_or_profesor`

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `user_id` | `int` | ID del usuario |

**Response `200`:** Ver objeto `UserResponse` arriba.

**Errores:**
- `404` — Usuario no encontrado

---

#### `POST /api/users/`

Crea un nuevo usuario (profesor o estudiante).

**Auth requerida:** `require_admin_or_profesor`

**Request Body:**

```json
{
  "name": "Ana",
  "last_name": "López",
  "email": "ana@ejemplo.com",
  "password": "pass123",
  "role": "profesor",
  "activation_code": "A1B2C3D4"
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `name` | `string` | ✅ | Nombre |
| `last_name` | `string` | ✅ | Apellido |
| `email` | `string (email)` | ✅ | Email único |
| `password` | `string` | ✅ | Contraseña |
| `role` | `string` | ✅ | `"profesor"` o `"estudiante"` |
| `activation_code` | `string` | ✅ | Código del circuito al que se asocia |

**Response `201`:** Ver objeto `UserResponse`.

**Reglas de rol:**
- `admin` puede crear `profesor` o `estudiante`
- `profesor` solo puede crear `estudiante`

**Errores:**
- `400` — Código de activación inválido o expirado
- `403` — Los profesores solo pueden crear cuentas de tipo `estudiante`
- `409` — Ya existe un usuario con ese email

---

#### `PUT /api/users/{user_id}`

Actualiza datos de un usuario.

**Auth requerida:** `require_admin`

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `user_id` | `int` | ID del usuario a actualizar |

**Request Body (todos opcionales):**

```json
{
  "name": "Ana",
  "last_name": "Martínez",
  "email": "nueva@ejemplo.com",
  "password": "nuevapass",
  "role": "profesor"
}
```

**Response `200`:** Ver objeto `UserResponse`.

**Errores:**
- `404` — Usuario no encontrado
- `409` — Ya existe un usuario con ese email

---

#### `DELETE /api/users/{user_id}`

Elimina un usuario.

**Auth requerida:** `require_admin`

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `user_id` | `int` | ID del usuario a eliminar |

**Response `204`:** Sin cuerpo.

**Errores:**
- `404` — Usuario no encontrado

---

### Circuits

Prefijo: `/api/circuits`

---

#### `POST /api/circuits/`

Crea un nuevo circuito con código de activación generado automáticamente.

**Auth requerida:** No

> **Nota:** Este endpoint lo usa el equipo de instalación al configurar un nuevo hardware. El código generado se imprime en el dispositivo físico.

**Response `201`:**

```json
{
  "id": 3,
  "activation_code": "A1B2C3D4",
  "created_at": "2024-01-15T10:00:00"
}
```

---

#### `GET /api/circuits/me`

Retorna el circuito asociado al usuario autenticado.

**Auth requerida:** `require_any_role`

**Response `200`:**

```json
{
  "id": 3,
  "activation_code": "A1B2C3D4",
  "is_active": true,
  "motor_on": false,
  "pump_on": false,
  "sensor_alcohol_on": true,
  "sensor_density_on": true,
  "sensor_conductivity_on": false,
  "sensor_ph_on": true,
  "sensor_temperature_on": true,
  "sensor_turbidity_on": false,
  "sensor_rpm_on": true,
  "activated_at": "2024-01-16T08:30:00",
  "created_at": "2024-01-15T10:00:00",
  "active_sensors": ["alcohol", "density", "ph", "temperature", "rpm"]
}
```

**Errores:**
- `404` — El usuario no tiene circuito asignado

---

#### `GET /api/circuits/{circuit_id}`

Obtiene un circuito por su ID.

**Auth requerida:** `require_admin_or_profesor`

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `circuit_id` | `int` | ID del circuito |

**Response `200`:** Ver objeto `CircuitResponse` arriba.

**Errores:**
- `404` — Circuito no encontrado

---

### Sensors

Prefijo: `/api/sensors`

---

#### `GET /api/sensors/{circuit_id}/{sensor_type}/history`

Obtiene el historial de lecturas de un sensor específico.

**Auth requerida:** `require_any_role`

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `circuit_id` | `int` | ID del circuito |
| `sensor_type` | `string` | Tipo de sensor (ver tipos válidos abajo) |

**Query Params:**

| Param | Tipo | Requerido | Descripción |
|---|---|---|---|
| `session_id` | `int` | No | Filtra por sesión de fermentación |
| `from_dt` | `datetime` | No | Fecha/hora de inicio del rango |
| `to_dt` | `datetime` | No | Fecha/hora de fin del rango |

**Tipos de sensor válidos:** `alcohol`, `density`, `conductivity`, `ph`, `temperature`, `turbidity`, `rpm`

**Response `200`:**

```json
{
  "circuit_id": 3,
  "sensor_type": "temperature",
  "readings": [
    {
      "id": 101,
      "circuit_id": 3,
      "sensor_type": "temperature",
      "value": 24.5,
      "session_id": 7,
      "timestamp": "2024-01-16T10:15:00"
    }
  ]
}
```

**Errores:**
- `400` — Tipo de sensor inválido

---

#### `GET /api/sensors/{circuit_id}/{sensor_type}/latest`

Obtiene la última lectura registrada de un sensor.

**Auth requerida:** `require_any_role`

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `circuit_id` | `int` | ID del circuito |
| `sensor_type` | `string` | Tipo de sensor |

**Response `200`:**

```json
{
  "id": 101,
  "circuit_id": 3,
  "sensor_type": "temperature",
  "value": 24.5,
  "session_id": 7,
  "timestamp": "2024-01-16T10:15:00"
}
```

Retorna `null` si no hay lecturas registradas.

---

### Fermentation

Prefijo: `/api/fermentation`

---

#### `POST /api/fermentation/schedule`

Programa una nueva sesión de fermentación.

**Auth requerida:** `require_admin_or_profesor`

**Request Body:**

```json
{
  "circuit_id": 3,
  "scheduled_start": "2024-01-17T08:00:00",
  "scheduled_end": "2024-01-17T20:00:00",
  "initial_sugar": 150.5
}
```

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `circuit_id` | `int` | ✅ | ID del circuito |
| `scheduled_start` | `datetime` | ✅ | Hora de inicio programada |
| `scheduled_end` | `datetime` | ✅ | Hora de fin programada (debe ser > `scheduled_start`) |
| `initial_sugar` | `float` | ✅ | Concentración inicial de azúcar (g/L) |

**Response `201`:**

```json
{
  "id": 7,
  "circuit_id": 3,
  "user_id": 1,
  "formula_id": 1,
  "scheduled_start": "2024-01-17T08:00:00",
  "scheduled_end": "2024-01-17T20:00:00",
  "actual_start": null,
  "actual_end": null,
  "status": "scheduled",
  "interrupted_by": null,
  "created_at": "2024-01-16T12:00:00"
}
```

**Errores:**
- `400` — La hora de fin debe ser mayor a la hora de inicio
- `409` — Ya hay una fermentación en curso para este circuito

---

#### `POST /api/fermentation/{session_id}/start`

Inicia una sesión de fermentación programada.

**Auth requerida:** `require_admin_or_profesor`

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `session_id` | `int` | ID de la sesión |

**Response `200`:** Ver `FermentationSessionResponse` con `status: "running"` y `actual_start` poblado.

**Comportamiento:**
- Registra lecturas iniciales de todos los sensores activos del circuito.
- Arranca los hilos de sensores en `SensorThreadManager`.

**Errores:**
- `400` — La sesión no está en estado `scheduled`
- `404` — Sesión no encontrada
- `409` — La fermentación ya está en curso

---

#### `POST /api/fermentation/{session_id}/stop`

Detiene una sesión de fermentación en curso.

**Auth requerida:** `require_admin_or_profesor`

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `session_id` | `int` | ID de la sesión |

**Request Body:**

```json
{
  "interrupted": false
}
```

| Campo | Tipo | Descripción |
|---|---|---|
| `interrupted` | `bool` | `true` = interrumpida por el usuario, `false` = completada normalmente |

**Response `200`:** Ver `FermentationSessionResponse` con `status: "completed"` o `"interrupted"`.

**Comportamiento:**
- Registra lecturas finales de todos los sensores activos.
- Calcula eficiencia de fermentación usando la fórmula activa.
- Genera entrada en `report_history`.
- Detiene todos los hilos de sensores del circuito.

**Fórmula de eficiencia:**
```
eficiencia = (etanol_detectado / (azucar_inicial × factor_conversion)) × 100
```
Limitada a 100%. El `factor_conversion` por defecto es `0.51` (Gay-Lussac).

**Errores:**
- `400` — La sesión no está en estado `running`
- `404` — Sesión no encontrada

---

#### `GET /api/fermentation/{session_id}/report`

Obtiene el reporte de una sesión de fermentación.

**Auth requerida:** `require_any_role`

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `session_id` | `int` | ID de la sesión |

**Response `200`:**

```json
{
  "id": 5,
  "session_id": 7,
  "initial_sugar": 150.5,
  "final_sugar": null,
  "ethanol_detected": 68.2,
  "theoretical_ethanol": 76.75,
  "efficiency": 88.86,
  "alcohol_initial": 0.0,
  "alcohol_final": 68.2,
  "temperature_initial": 22.0,
  "temperature_final": 25.5,
  "notes": null,
  "generated_at": "2024-01-17T20:05:00"
}
```

> Incluye lecturas iniciales, finales y timestamp de desactivación para cada sensor (`alcohol`, `density`, `conductivity`, `ph`, `temperature`, `turbidity`, `rpm`).

> Acceder al reporte registra automáticamente un evento `"viewed"` en `report_history`.

**Errores:**
- `404` — Reporte no encontrado

---

#### `GET /api/fermentation/history`

Obtiene el historial de reportes del usuario autenticado.

**Auth requerida:** `require_any_role`

**Response `200`:**

```json
[
  {
    "id": 10,
    "report_id": 5,
    "user_id": 1,
    "action": "viewed",
    "occurred_at": "2024-01-18T09:00:00"
  }
]
```

**Valores de `action`:** `"generated"`, `"downloaded"`, `"viewed"`

---

### Notifications

Prefijo: `/api/notifications`

---

#### `GET /api/notifications/`

Lista las notificaciones del usuario autenticado.

**Auth requerida:** `require_any_role` (cualquier usuario autenticado)

**Query Params:**

| Param | Tipo | Default | Descripción |
|---|---|---|---|
| `only_unread` | `bool` | `false` | Si es `true`, solo retorna notificaciones no leídas |

**Response `200`:**

```json
[
  {
    "id": 1,
    "user_id": 1,
    "message": "⚠️ Temperatura crítica: 42.5°C (umbral: 40.0°C)",
    "type": "high_temperature",
    "status": "unread",
    "session_id": 7,
    "created_at": "2024-01-17T14:30:00"
  }
]
```

**Tipos de notificación:** `fermentation_complete`, `fermentation_interrupted`, `high_temperature`, `sensor_failure`, `general`

---

#### `PATCH /api/notifications/{notification_id}/read`

Marca una notificación específica como leída.

**Auth requerida:** `require_any_role`

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `notification_id` | `int` | ID de la notificación |

**Response `200`:** Objeto `NotificationResponse` con `status: "read"`.

---

#### `PATCH /api/notifications/read-all`

Marca todas las notificaciones del usuario autenticado como leídas.

**Auth requerida:** `require_any_role`

**Response `204`:** Sin cuerpo.

---

### Formula

Prefijo: `/api/formula`

La fórmula de eficiencia determina el factor de conversión usado para calcular el rendimiento de la fermentación.

---

#### `GET /api/formula/active`

Obtiene la fórmula de eficiencia activa.

**Auth requerida:** Cualquier usuario autenticado

**Response `200`:**

```json
{
  "id": 1,
  "name": "Fórmula estándar Gay-Lussac",
  "conversion_factor": 0.51,
  "description": "eficiencia = (etanol_sensor / (azucar_inicial * factor)) * 100",
  "is_active": true,
  "updated_by": null,
  "updated_at": "2024-01-15T10:00:00",
  "created_at": "2024-01-15T10:00:00"
}
```

**Errores:**
- `404` — No hay ninguna fórmula activa

---

#### `GET /api/formula/`

Lista todas las fórmulas registradas.

**Auth requerida:** Cualquier usuario autenticado

**Response `200`:** Array de `FormulaResponse`.

---

#### `GET /api/formula/{formula_id}`

Obtiene una fórmula por su ID.

**Auth requerida:** Cualquier usuario autenticado

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `formula_id` | `int` | ID de la fórmula |

**Response `200`:** Ver `FormulaResponse`.

**Errores:**
- `404` — Fórmula no encontrada

---

#### `PUT /api/formula/{formula_id}`

Edita una fórmula existente.

**Auth requerida:** `require_admin_or_profesor`

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `formula_id` | `int` | ID de la fórmula |

**Request Body (todos opcionales):**

```json
{
  "name": "Fórmula ajustada",
  "conversion_factor": 0.48,
  "description": "Factor ajustado para sustrato alternativo"
}
```

> El `conversion_factor` debe ser mayor a `0`.

**Response `200`:** Ver `FormulaResponse`.

**Errores:**
- `400` — El factor de conversión debe ser mayor a 0
- `404` — Fórmula no encontrada

---

#### `PATCH /api/formula/{formula_id}/activate`

Cambia la fórmula activa del sistema. Solo puede haber una fórmula activa a la vez.

**Auth requerida:** `require_admin_or_profesor`

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `formula_id` | `int` | ID de la fórmula a activar |

**Response `200`:** Ver `FormulaResponse` con `is_active: true`.

**Errores:**
- `404` — Fórmula no encontrada

---

### Health

#### `GET /health`

Verifica el estado de los servicios del backend.

**Auth requerida:** No

**Response `200`:**

```json
{
  "status": "ok",
  "database": "connected",
  "rabbitmq": "connected"
}
```

**Valores posibles de `rabbitmq`:** `"connected"`, `"disconnected"`

---

## WebSockets

### WS Sensors

#### `WS /ws/sensors/{circuit_id}`

Canal unidireccional **Back → Front** para lecturas de sensores en tiempo real.

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `circuit_id` | `int` | ID del circuito a escuchar |

**Mensajes recibidos:**

**`sensor_data`** — Nueva lectura de sensor:

```json
{
  "type": "sensor_data",
  "sensor_type": "temperature",
  "value": 25.3,
  "circuit_id": 3,
  "session_id": 7,
  "timestamp": "2024-01-17T10:15:30",
  "active": true
}
```

**`sensor_deactivated`** — Sensor desactivado durante fermentación:

```json
{
  "type": "sensor_deactivated",
  "sensor_type": "alcohol",
  "circuit_id": 3,
  "session_id": 7,
  "last_reading": 65.2,
  "occurred_at": "2024-01-17T15:00:00"
}
```

---

### WS Notifications

#### `WS /ws/notifications/{user_id}`

Canal unidireccional **Back → Front** para notificaciones en tiempo real.

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `user_id` | `int` | ID del usuario que recibirá notificaciones |

**Mensajes recibidos:**

```json
{
  "type": "high_temperature",
  "notification_id": 42,
  "message": "⚠️ Temperatura crítica: 42.5°C (umbral: 40.0°C)",
  "session_id": 7,
  "occurred_at": "2024-01-17T14:30:00"
}
```

**Tipos de notificación:** `fermentation_complete`, `fermentation_interrupted`, `high_temperature`, `sensor_failure`, `general`

**Alerta automática de temperatura:** Se dispara automáticamente cuando el sensor de temperatura supera el umbral configurado (`TEMPERATURE_ALERT_THRESHOLD`, default `40.0°C`).

---

### WS Circuit Commands

#### `WS /ws/circuit/{circuit_id}/commands`

Canal bidireccional **Front → Back → RabbitMQ → ESP32** para control del circuito.

**Path Params:**

| Param | Tipo | Descripción |
|---|---|---|
| `circuit_id` | `int` | ID del circuito a controlar |

**Mensajes enviados (Front → Back):**

El frontend envía el estado deseado de los dispositivos como JSON libre:

```json
{
  "motor": "encendido",
  "bomba": "apagado"
}
```

El backend publica el mensaje en RabbitMQ con routing key `commands.{circuit_id}.state`. El ESP32 lo recibe por MQTT en el topic `commands/{circuit_id}/state`.

**Respuesta de confirmación (Back → Front):**

```json
{
  "status": "ok",
  "payload": {
    "motor": "encendido",
    "bomba": "apagado"
  }
}
```

---

## Modelos de datos

### User

```json
{
  "id": 1,
  "name": "Juan",
  "last_name": "García",
  "email": "juan@ejemplo.com",
  "role_id": 1,
  "role_name": "admin",
  "circuit_id": 3,
  "created_by": null,
  "created_at": "2024-01-15T10:00:00"
}
```

### Circuit

```json
{
  "id": 3,
  "activation_code": "A1B2C3D4",
  "is_active": true,
  "motor_on": false,
  "pump_on": false,
  "sensor_alcohol_on": true,
  "sensor_density_on": true,
  "sensor_conductivity_on": false,
  "sensor_ph_on": true,
  "sensor_temperature_on": true,
  "sensor_turbidity_on": false,
  "sensor_rpm_on": true,
  "activated_at": "2024-01-16T08:30:00",
  "created_at": "2024-01-15T10:00:00",
  "active_sensors": ["alcohol", "density", "ph", "temperature", "rpm"]
}
```

### FermentationSession

```json
{
  "id": 7,
  "circuit_id": 3,
  "user_id": 1,
  "formula_id": 1,
  "scheduled_start": "2024-01-17T08:00:00",
  "scheduled_end": "2024-01-17T20:00:00",
  "actual_start": "2024-01-17T08:05:00",
  "actual_end": "2024-01-17T19:55:00",
  "status": "completed",
  "interrupted_by": null,
  "created_at": "2024-01-16T12:00:00"
}
```

**Estados posibles de `status`:** `scheduled`, `running`, `completed`, `interrupted`

### SensorReading

```json
{
  "id": 101,
  "circuit_id": 3,
  "sensor_type": "temperature",
  "value": 24.5,
  "session_id": 7,
  "timestamp": "2024-01-17T10:15:00"
}
```

### Notification

```json
{
  "id": 1,
  "user_id": 1,
  "message": "⚠️ Temperatura crítica: 42.5°C",
  "type": "high_temperature",
  "status": "unread",
  "session_id": 7,
  "created_at": "2024-01-17T14:30:00"
}
```

---

## Esquema de base de datos

```
roles
├── id (PK)
├── name
└── description

users
├── id (PK)
├── name, last_name, email, password
├── role_id → roles.id
├── circuit_id → circuits.id
├── created_by → users.id
└── created_at

circuits
├── id (PK)
├── activation_code (UNIQUE)
├── is_active, activated_at
├── motor_on, pump_on
├── sensor_alcohol_on, sensor_density_on, sensor_conductivity_on
├── sensor_ph_on, sensor_temperature_on, sensor_turbidity_on, sensor_rpm_on
└── created_at

efficiency_formula
├── id (PK)
├── name, conversion_factor (default: 0.51), description
├── is_active
├── updated_by → users.id
└── updated_at, created_at

fermentation_sessions
├── id (PK)
├── circuit_id → circuits.id
├── user_id → users.id
├── formula_id → efficiency_formula.id
├── scheduled_start, scheduled_end
├── actual_start, actual_end
├── status: ENUM(scheduled, running, completed, interrupted)
├── interrupted_by → users.id
└── created_at

fermentation_reports
├── id (PK)
├── session_id → fermentation_sessions.id (UNIQUE)
├── initial_sugar, final_sugar
├── ethanol_detected, theoretical_ethanol, efficiency
├── {sensor}_initial, {sensor}_final, {sensor}_deactivated_at, {sensor}_last_reading
│   (para: alcohol, density, conductivity, ph, temperature, turbidity, rpm)
├── notes
└── generated_at

report_history
├── id (PK)
├── report_id → fermentation_reports.id
├── user_id → users.id
├── action: ENUM(generated, downloaded, viewed)
└── occurred_at

notifications
├── id (PK)
├── user_id → users.id
├── session_id → fermentation_sessions.id
├── type: ENUM(fermentation_complete, fermentation_interrupted, high_temperature, sensor_failure, general)
├── message, status: ENUM(unread, read)
└── created_at

Tablas de sensores (misma estructura para todas):
alcohol_sensor / density_sensor / conductivity_sensor / ph_sensor /
temperature_sensor / turbidity_sensor / motor_rpm_sensor
├── measurement_id (PK)
├── circuit_id → circuits.id
├── session_id → fermentation_sessions.id
├── timestamp
└── {valor_del_sensor} (float)
```

---

## Configuración e infraestructura

### Docker Compose

El proyecto incluye tres servicios:

| Servicio | Puerto | Descripción |
|---|---|---|
| `api` | `8000` | FastAPI backend |
| `mysql` | `3307` | Base de datos MySQL 8.0 |
| `adminer` | `8080` | Interfaz web para administrar MySQL |

**Levantar el stack:**

```bash
docker-compose up --build
```

La API espera 15 segundos para que MySQL esté disponible antes de arrancar.

### Mensajería RabbitMQ

El sistema usa dos protocolos de mensajería:

| Exchange | Tipo | Dirección | Descripción |
|---|---|---|---|
| `sensor.data` | TOPIC | ESP32 → Back (AMQP) | Lecturas directas desde dispositivos AMQP |
| `amq.topic` | TOPIC | ESP32 → Back (MQTT) | Lecturas desde ESP32 vía MQTT |
| `amq.topic` | TOPIC | Back → ESP32 (MQTT) | Comandos de control al hardware |

**Routing keys MQTT:**

| Dirección | Formato | Ejemplo |
|---|---|---|
| Lecturas (ESP32 → Back) | `sensors.{circuit_id}.{sensor_type}` | `sensors.3.temperature` |
| Comandos (Back → ESP32) | `commands.{circuit_id}.state` | `commands.3.state` |

**Queues:**

| Queue | TTL | Max length | Descripción |
|---|---|---|---|
| `sensor.data.queue` | 60s | 10,000 | Lecturas AMQP |
| `mqtt.sensor.data.queue` | 60s | 10,000 | Lecturas MQTT |
| `circuit.commands.queue` | 30s | 1,000 | Comandos al ESP32 |

---

## Variables de entorno

Crear un archivo `.env` con las siguientes variables:

```env
# Aplicación
APP_NAME=sensor_db_backend
APP_ENV=development
DEBUG=true

# JWT
SECRET_KEY=tu_clave_secreta_muy_larga_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# MySQL
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_password
DB_NAME=sensor_db

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
```

| Variable | Default | Descripción |
|---|---|---|
| `SECRET_KEY` | — | Clave para firmar los JWT (**obligatorio**) |
| `ALGORITHM` | `HS256` | Algoritmo de firma JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Duración del access token en minutos |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Duración del refresh token en días |
| `DB_HOST` | — | Host de MySQL (**obligatorio**) |
| `DB_PORT` | — | Puerto de MySQL (**obligatorio**) |
| `DB_USER` | — | Usuario de MySQL (**obligatorio**) |
| `DB_PASSWORD` | — | Contraseña de MySQL (**obligatorio**) |
| `DB_NAME` | — | Nombre de la base de datos (**obligatorio**) |
| `RABBITMQ_HOST` | — | Host de RabbitMQ (**obligatorio**) |
| `RABBITMQ_PORT` | — | Puerto de RabbitMQ (**obligatorio**) |
| `RABBITMQ_USER` | — | Usuario de RabbitMQ (**obligatorio**) |
| `RABBITMQ_PASSWORD` | — | Contraseña de RabbitMQ (**obligatorio**) |
| `TEMPERATURE_ALERT_THRESHOLD` | `40.0` | Umbral de temperatura para alertas (°C) |

> **Nota:** Si RabbitMQ no está disponible al iniciar, el backend continúa funcionando. Los endpoints REST y WebSocket operan normalmente; solo las lecturas en tiempo real de sensores estarán deshabilitadas.