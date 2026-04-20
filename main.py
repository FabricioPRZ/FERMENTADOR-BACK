import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    logger.info("Iniciando aplicación...")

    # 1. Base de datos (siempre requerida)
    from core.database import init_db
    await init_db()
    logger.info("Base de datos inicializada")

    # 2. RabbitMQ (opcional hasta tener EC2)
    rabbitmq_available = False
    try:
        from core.rabbitmq.connection import rabbitmq
        await rabbitmq.connect()

        from core.rabbitmq.exchanges import exchange_manager
        await exchange_manager.setup()

        from core.rabbitmq.consumer import consumer
        from modules.sensors.application.usecase.save_reading_use_case import SaveReadingUseCase
        from modules.sensors.infrastructure.adapters.MySQL import SensorRepository
        from modules.notifications.application.usecase.send_notification_use_case import SendNotificationUseCase
        from modules.notifications.infrastructure.adapters.MySQL import NotificationRepository
        from modules.fermentation.infrastructure.adapters.MySQL import FermentationRepository
        from core.database import AsyncSessionLocal

        consumer.set_dependencies(
            save_reading_use_case=SaveReadingUseCase(
                SensorRepository(AsyncSessionLocal)
            ),
            send_notification_use_case=SendNotificationUseCase(
                NotificationRepository(AsyncSessionLocal)
            ),
            fermentation_repository=FermentationRepository(AsyncSessionLocal),
        )

        from core.threads.sensor_thread_manager import thread_manager
        from modules.sensors.infrastructure.adapters.sensor_thread import SensorThread
        thread_manager.set_thread_class(SensorThread)

        await consumer.start()

        rabbitmq_available = True
        logger.info("RabbitMQ conectado y consumer iniciado")

    except Exception as e:
        logger.warning(
            f"RabbitMQ no disponible, continuando sin broker: {e}\n"
            "Los endpoints REST y WebSocket funcionan normalmente.\n"
            "Los datos de sensores en tiempo real estarán deshabilitados."
        )

    logger.info("Aplicación lista")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Cerrando aplicación...")

    if rabbitmq_available:
        from core.rabbitmq.consumer import consumer
        from core.rabbitmq.connection import rabbitmq
        from core.threads.sensor_thread_manager import thread_manager

        await consumer.stop()
        thread_manager.stop_all()
        await rabbitmq.disconnect()
        logger.info("RabbitMQ desconectado")

    logger.info("Aplicación cerrada correctamente")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Sensor DB Backend",
    description="API para monitoreo de fermentación con ESP32",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
from modules.auth.infrastructure.routes.router             import router as auth_router
from modules.users.infrastructure.routes.router            import router as users_router
from modules.circuits.infrastructure.routes.router         import router as circuits_router
from modules.circuits.infrastructure.routes.websocket      import router as circuits_ws_router
from modules.sensors.infrastructure.routes.router          import router as sensors_router
from modules.sensors.infrastructure.routes.websocket       import router as sensors_ws_router
from modules.fermentation.infrastructure.routes.router     import router as fermentation_router
from modules.notifications.infrastructure.routes.router    import router as notifications_router
from modules.notifications.infrastructure.routes.websocket import router as notifications_ws_router
from modules.formula.infrastructure.routes.router          import router as formula_router

app.include_router(auth_router,             prefix="/api/auth",          tags=["Auth"])
app.include_router(users_router,            prefix="/api/users",         tags=["Users"])
app.include_router(circuits_router,         prefix="/api/circuits",      tags=["Circuits"])
app.include_router(circuits_ws_router,      prefix="",                   tags=["Circuits WS"])
app.include_router(sensors_router,          prefix="/api/sensors",       tags=["Sensors"])
app.include_router(sensors_ws_router,       prefix="",                   tags=["Sensors WS"])
app.include_router(fermentation_router,     prefix="/api/fermentation",  tags=["Fermentation"])
app.include_router(notifications_router,    prefix="/api/notifications", tags=["Notifications"])
app.include_router(notifications_ws_router, prefix="",                   tags=["Notifications WS"])
app.include_router(formula_router,          prefix="/api/formula",       tags=["Formula"])


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    from core.rabbitmq.connection import rabbitmq
    rabbit_status = "connected"
    try:
        if rabbitmq._connection is None or rabbitmq._connection.is_closed:
            rabbit_status = "disconnected"
    except Exception:
        rabbit_status = "disconnected"

    return {
        "status":   "ok",
        "database": "connected",
        "rabbitmq": rabbit_status,
    }