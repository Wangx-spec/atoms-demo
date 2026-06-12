from fastapi import APIRouter, WebSocket

router = APIRouter()


@router.websocket("/events")
async def websocket_events(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json({"type": "connected", "message": "Atoms realtime channel ready"})
    await websocket.close()
