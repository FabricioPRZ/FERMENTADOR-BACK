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
            raw  = await websocket.receive_text()
            data = json.loads(raw)

            # El front manda: { "command_type": "motor_on", "payload": {} }
            # CommandMessage usa el campo "type" internamente
            command = CommandMessage(
                type=data.get("command_type"),
                target=data.get("target", "device"),
                circuit_id=circuit_id,
            )

            await publisher.publish_command(command)

            # Respuesta al front y al ESP32:
            # { "status": "ok", "command": "motor_on" }
            await websocket.send_text(
                json.dumps({"status": "ok", "command": command.type})
            )

    except WebSocketDisconnect:
        logger.info(
            f"[WS:Commands] Cliente desconectado → circuit_id={circuit_id}"
        )

    except Exception as e:
        logger.error(
            f"[WS:Commands] Error → circuit_id={circuit_id} | {e}"
        )
        try:
            await websocket.close()
        except Exception:
            pass