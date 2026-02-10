from typing import List, Dict, Any, Optional
from app.services.sheets_service import SheetsService
from app.services.assignment_service import AssignmentService
from app.services.conflict_detector import ConflictDetector

class ToolExecutor:
    def __init__(self):
        # Initialize services
        self.sheets = SheetsService()
        self.assignment_service = AssignmentService()
        self.conflict_detector = ConflictDetector()

    def get_available_pilots(self, skills: Optional[List[str]] = None, location: Optional[str] = None) -> str:
        """
        Get list of available pilots, optionally filtered by skills and location.
        
        Args:
            skills: Required skills (e.g., ['commercial', 'night_flying'])
            location: Required location
        """
        pilots = self.sheets.get_all_pilots()
        
        # Filter by skills if provided
        if skills:
            required_skills = set(skills)
            pilots = [p for p in pilots if required_skills.issubset(set(p.skills))]
        
        # Filter by location if provided
        if location:
            pilots = [p for p in pilots if p.location == location]
        
        # Filter only available
        pilots = [p for p in pilots if p.status == "available"]
        
        if not pilots:
            return "No available pilots found matching criteria"
        
        result = "Available Pilots:\n"
        for p in pilots:
            result += f"- {p.name} (ID: {p.pilot_id})\n"
            result += f"  Skills: {', '.join(p.skills)}\n"
            result += f"  Location: {p.location}\n"
            result += f"  Certs: {', '.join(p.certifications)}\n\n"
        
        return result

    def get_available_drones(self, capabilities: Optional[List[str]] = None, location: Optional[str] = None) -> str:
        """
        Get list of available drones, optionally filtered by capabilities and location.
        
        Args:
            capabilities: Required drone capabilities
            location: Required location
        """
        drones = self.sheets.get_all_drones()
        
        # Filter by capabilities if provided
        if capabilities:
            required_caps = set(capabilities)
            drones = [d for d in drones if required_caps.issubset(set(d.capabilities))]
        
        # Filter by location if provided
        if location:
            drones = [d for d in drones if d.location == location]
        
        # Filter only available
        drones = [d for d in drones if d.status == "available"]
        
        if not drones:
            return "No available drones found matching criteria"
        
        result = "Available Drones:\n"
        for d in drones:
            result += f"- {d.model} (ID: {d.drone_id})\n"
            result += f"  Capabilities: {', '.join(d.capabilities)}\n"
            result += f"  Location: {d.location}\n\n"
        
        return result

    def assign_pilot_to_mission(self, mission_id: str) -> str:
        """
        Assign a pilot and drone to a mission with conflict detection.
        
        Args:
            mission_id: Mission/project ID to assign resources to
        """
        result = self.assignment_service.assign_mission(mission_id)
        
        if result.success:
            return f"✅ {result.message}\nPilot: {result.assigned_pilot}\nDrone: {result.assigned_drone}"
        else:
            conflicts_str = "\n".join(f"- {c}" for c in result.conflicts)
            return f"❌ {result.message}\n\nConflicts:\n{conflicts_str}"

    def check_mission_conflicts(self, mission_id: str) -> str:
        """
        Check for conflicts in a specific mission assignment.
        
        Args:
            mission_id: Mission ID to check
        """
        mission = self.sheets.get_mission_by_id(mission_id)
        
        if not mission:
            return f"Mission {mission_id} not found"
        
        pilots = self.sheets.get_all_pilots()
        drones = self.sheets.get_all_drones()
        
        conflicts = []
        
        for pilot in pilots:
            check = self.conflict_detector.check_pilot_availability(pilot, mission)
            if not check.has_conflict:
                conflicts.append(f"✅ Pilot {pilot.name} is suitable")
        
        for drone in drones:
            check = self.conflict_detector.check_drone_availability(drone, mission)
            if not check.has_conflict:
                conflicts.append(f"✅ Drone {drone.drone_id} is suitable")
        
        return "\n".join(conflicts) if conflicts else "No suitable resources found"

    def update_pilot_status(self, pilot_id: str, status: str) -> str:
        """
        Update a pilot's status (available, assigned, on_leave, training).
        
        Args:
            pilot_id: Pilot ID
            status: New status (available, assigned, on_leave, training)
        """
        success = self.sheets.update_pilot_status(pilot_id, status)
        
        if success:
            return f"✅ Updated pilot {pilot_id} status to {status}"
        else:
            return f"❌ Failed to update pilot {pilot_id}"

    def get_all_missions(self) -> str:
        """Get all current missions."""
        missions = self.sheets.get_all_missions()
        
        if not missions:
            return "No missions found"
        
        result = "Current Missions:\n"
        for m in missions:
            result += f"\n- {m.client} (ID: {m.project_id})\n"
            result += f"  Location: {m.location}\n"
            # Format dates to string
            start_str = m.start_date.strftime('%Y-%m-%d') if hasattr(m.start_date, 'strftime') else m.start_date
            end_str = m.end_date.strftime('%Y-%m-%d') if hasattr(m.end_date, 'strftime') else m.end_date
            
            result += f"  Dates: {start_str} to {end_str}\n"
            result += f"  Priority: {m.priority}\n"
            result += f"  Required Skills: {', '.join(m.required_skills)}\n"
        
        return result

# Initialize the executor
executor = ToolExecutor()

# Define the TOOLS list as the actual Python functions.
# The SDK uses the function names and docstrings to explain them to the AI.
TOOLS = [
    executor.get_available_pilots,
    executor.get_available_drones,
    executor.assign_pilot_to_mission,
    executor.check_mission_conflicts,
    executor.update_pilot_status,
    executor.get_all_missions
]