from typing import Any, Dict, List

import httpx
import structlog

logger = structlog.get_logger(__name__)


class UnityBridgeClient:
    """SOTA Unity Editor Bridge Client.
    Communicates with the C# Bridge script running inside Unity Editor.
    """

    def __init__(self, host: str = "localhost", port: int = 10835):
        self.url = f"http://{host}:{port}"
        self.timeout = 5.0

    async def is_alive(self) -> bool:
        """Check if the Unity Editor Bridge is reachable."""
        try:
            async with httpx.AsyncClient(timeout=1.0) as client:
                response = await client.post(f"{self.url}/", json={"action": "ping"})
                return response.status_code == 200
        except Exception:
            return False

    async def execute_command(self, action: str, target: str = None, **kwargs) -> Dict[str, Any]:
        """Send a JSON command to the Unity Editor Bridge."""
        payload = {"action": action, "target": target, **kwargs}
        logger.debug("unity3d.bridge.command_sent", action=action, target=target)

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.url}/", json=payload)
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error("unity3d.bridge.error", status_code=response.status_code, text=response.text)
                    return {"error": f"Bridge returned status {response.status_code}", "details": response.text}
        except httpx.ConnectError:
            return {"error": "Unity Editor Bridge not found. Is Unity running with MCPBridge.cs installed?"}
        except Exception as e:
            logger.exception("unity3d.bridge.exception")
            return {"error": str(e)}

    # High-level helper methods
    async def get_hierarchy(self) -> Dict[str, Any]:
        return await self.execute_command("get_hierarchy")

    async def get_components(self, target: str) -> Dict[str, Any]:
        return await self.execute_command("get_components", target=target)

    async def transform_object(
        self,
        target: str,
        position: List[float] = None,
        rotation: List[float] = None,
        scale: List[float] = None,
    ) -> Dict[str, Any]:
        return await self.execute_command(
            "set_transform",
            target=target,
            position=position,
            rotation=rotation,
            scale=scale,
        )

    async def create_object(self, name: str, type: str = "GameObject") -> Dict[str, Any]:
        return await self.execute_command("create_object", name=name, type=type)

    async def create_primitive(
        self,
        name: str,
        primitive_type: str = "Cube",
        position: List[float] = None,
        rotation: List[float] = None,
        scale: List[float] = None,
    ) -> Dict[str, Any]:
        return await self.execute_command(
            "create_primitive",
            name=name,
            primitiveType=primitive_type,
            position=position,
            rotation=rotation,
            scale=scale,
        )

    async def add_component(self, target: str, component_type: str) -> Dict[str, Any]:
        return await self.execute_command("add_component", target=target, componentType=component_type)

    async def delete_object(self, target: str) -> Dict[str, Any]:
        return await self.execute_command("delete_object", target=target)

    async def save_scene(self) -> Dict[str, Any]:
        return await self.execute_command("save_scene")

    async def get_console_counts(self) -> Dict[str, Any]:
        return await self.execute_command("get_console_counts")

    async def clear_console(self) -> Dict[str, Any]:
        return await self.execute_command("clear_console")

    async def get_editor_state(self) -> Dict[str, Any]:
        return await self.execute_command("get_editor_state")

    async def refresh_assets(self) -> Dict[str, Any]:
        return await self.execute_command("refresh_assets")

    async def open_scene(self, scene_path: str, force: bool = False) -> Dict[str, Any]:
        return await self.execute_command("open_scene", path=scene_path, force=force)

    async def run_editmode_tests(self) -> Dict[str, Any]:
        return await self.execute_command("run_editmode_tests")

    async def get_test_status(self) -> Dict[str, Any]:
        return await self.execute_command("get_test_status")
