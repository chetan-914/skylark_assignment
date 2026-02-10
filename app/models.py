from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class PilotStatus(str, Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    ON_LEAVE = "on_leave"
    # TRAINING = "training"


class DroneStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    # RETIRED = "retired"


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Pilot(BaseModel):
    pilot_id: str
    name: str
    skills: List[str]
    certifications: List[str]
    location: str
    status: PilotStatus
    current_assignment: Optional[str] = None
    available_from: Optional[datetime] = None


class Drone(BaseModel):
    drone_id: str
    model: str
    capabilities: List[str]
    status: DroneStatus
    location: str
    current_assignment: Optional[str] = None
    maintenance_due: Optional[datetime] = None


class Mission(BaseModel):
    project_id: str
    client: str
    location: str
    required_skills: List[str]
    required_certs: List[str]
    start_date: datetime
    end_date: datetime
    priority: Priority


class AssignmentResult(BaseModel):
    success: bool
    message: str
    conflicts: List[str] = []
    assigned_pilot: Optional[str] = None
    assigned_drone: Optional[str] = None


class ConflictCheck(BaseModel):
    has_conflict: bool
    conflict_type: Optional[str] = None
    details: List[str] = []