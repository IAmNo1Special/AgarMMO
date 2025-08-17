import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List, Tuple, Type, TypeVar, ClassVar # Added ClassVar

T = TypeVar('T', bound='Packet')

@dataclass
class Packet:
    type: ClassVar[str] # Changed to ClassVar

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        # Ensure the 'type' field is always present in the dictionary for JSON serialization
        # as asdict might exclude ClassVar fields.
        data['type'] = self.type
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        data = json.loads(json_str)
        packet_type = data.pop('type') # Remove 'type' from data before passing to constructor
        if not packet_type:
            raise ValueError("Packet JSON missing 'type' field")

        # This is a simple factory. For a larger system, a more robust factory pattern
        # or a registry of packet types would be better.
        if packet_type == "connect":
            return ConnectPacket(**data)
        elif packet_type == "move":
            return MovePacket(**data)
        elif packet_type == "skill":
            return SkillPacket(**data)
        elif packet_type == "get_game_state":
            return GetGameStatePacket(**data)
        elif packet_type == "player_id":
            return PlayerIdPacket(**data)
        elif packet_type == "game_state":
            return GameStatePacket(**data)
        elif packet_type == "username_taken":
            return UsernameTakenPacket(**data)
        elif packet_type == "server_full":
            return ServerFullPacket(**data)
        elif packet_type == "ping":
            return PingPacket(**data)
        elif packet_type == "pong":
            return PongPacket(**data)
        else:
            raise ValueError(f"Unknown packet type: {packet_type}")

@dataclass
class ConnectPacket(Packet):
    name: str
    type: ClassVar[str] = "connect" # Changed to ClassVar

@dataclass
class MovePacket(Packet):
    dx: float
    dy: float
    type: ClassVar[str] = "move" # Changed to ClassVar

@dataclass
class SkillPacket(Packet):
    skill_name: str
    type: ClassVar[str] = "skill" # Changed to ClassVar

@dataclass
class GetGameStatePacket(Packet):
    type: ClassVar[str] = "get_game_state" # Changed to ClassVar

@dataclass
class PlayerIdPacket(Packet):
    player_id: str
    type: ClassVar[str] = "player_id" # Changed to ClassVar

@dataclass
class GameStatePacket(Packet):
    balls: List[Dict[str, Any]]
    players: Dict[str, Any]
    game_time: float
    type: ClassVar[str] = "game_state" # Changed to ClassVar

@dataclass
class UsernameTakenPacket(Packet):
    message: str
    type: ClassVar[str] = "username_taken" # Changed to ClassVar

@dataclass
class ServerFullPacket(Packet):
    message: str
    type: ClassVar[str] = "server_full" # Changed to ClassVar

@dataclass
class PingPacket(Packet):
    type: ClassVar[str] = "ping" # Changed to ClassVar

@dataclass
class PongPacket(Packet):
    type: ClassVar[str] = "pong" # Changed to ClassVar