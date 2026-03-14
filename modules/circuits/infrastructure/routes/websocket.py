import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.websocket.schemas import CommandMessage
from core.rabbitmq.publisher import publisher

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/ws/circuit/{circuit_id}/commands")
async def circuit_commands_ws(
    websocket: WebSocket,
    circuit_id: int,
):
    """
    Canal Front → Back → RabbitMQ para comandos al ESP32.
    El back actúa solo como puente, no persiste los comandos.
    """
    await websocket.accept()
    logger.info(f"[WS:Commands] Cliente conectado → circuit_id={circuit_id}")

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            command = CommandMessage(
                circuit_id=circuit_id,
                command_type=data.get("command_type"),
                payload=data.get("payload", {}),
            )

            await publisher.publish_command(command)
            await websocket.send_text(
                json.dumps({"status": "ok", "command": command.command_type})
            )

    except WebSocketDisconnect:
        logger.info(
            f"[WS:Commands] Cliente desconectado → circuit_id={circuit_id}"
        )

    except Exception as e:
        logger.error(
            f"[WS:Commands] Error → circuit_id={circuit_id} | {e}"
        )
        await websocket.close()