from typing import List, Dict, Any
from app.services.sheets_service import SheetsService
from app.services.assignment_service import AssignmentService
from app.services.conflict_detector import ConflictDetector


# Tool definitions for Gemini function calling
TOOLS = [
    {
        "name": "get_available_pilots",
        "description": "Get list of available pilots, optionally filtered by skills and location",
        "parameters": {
            "type": "object",
            "properties": {
                "skills": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Required skills (e.g., ['commercial', 'night_flying'])"
                },
                "location": {
                    "type": "string",
                    "description": "Required location"
                }
            }
        }
    },
    {
        "name": "get_available_drones",
        "description": "Get list of available drones, optionally filtered by capabilities and location",
        "parameters": {
            "type": "object",
            "properties": {
                "capabilities": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Required capabilities"
                },
                "location": {
                    "type": "string",
                    "description": "Required location"
                }
            }
        }
    },
    {
        "name": "assign_pilot_to_mission",
        "description": "Assign a pilot and drone to a mission with conflict detection",
        "parameters": {
            "type": "object",
            "properties": {
                "mission_id": {
                    "type": "string",
                    "description": "Mission/project ID to assign resources to"
                }
            },
            "required": ["mission_id"]
        }
    },
    {
        "name": "check_mission_conflicts",
        "description": "Check for conflicts in a specific mission assignment",
        "parameters": {
            "type": "object",
            "properties": {
                "mission_id": {
                    "type": "string",
                    "description": "Mission ID to check"
                }
            },
            "required": ["mission_id"]
        }
    },
    {
        "name": "update_pilot_status",
        "description": "Update a pilot's status (available, assigned, on_leave, training)",
        "parameters": {
            "type": "object",
            "properties": {
                "pilot_id": {
                    "type": "string",
                    "description": "Pilot ID"
                },
                "status": {
                    "type": "string",
                    "description": "New status",
                    "enum": ["available", "assigned", "on_leave", "training"]
                }
            },
            "required": ["pilot_id", "status"]
        }
    },
    {
        "name": "get_all_missions",
        "description": "Get all current missions",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]


class ToolExecutor:
    def __init__(self):
        self.sheets = SheetsService()
        self.assignment_service = AssignmentService()
        self.conflict_detector = ConflictDetector()
    
    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> str:
        """Execute a tool and return result as string"""
        
        if tool_name == "get_available_pilots":
            pilots = self.sheets.get_all_pilots()
            
            # Filter by skills if provided
            if "skills" in parameters and parameters["skills"]:
                required_skills = set(parameters["skills"])
                pilots = [p for p in pilots if required_skills.issubset(set(p.skills))]
            
            # Filter by location if provided
            if "location" in parameters and parameters["location"]:
                pilots = [p for p in pilots if p.location == parameters["location"]]
            
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
        
        elif tool_name == "get_available_drones":
            drones = self.sheets.get_all_drones()
            
            # Filter by capabilities if provided
            if "capabilities" in parameters and parameters["capabilities"]:
                required_caps = set(parameters["capabilities"])
                drones = [d for d in drones if required_caps.issubset(set(d.capabilities))]
            
            # Filter by location if provided
            if "location" in parameters and parameters["location"]:
                drones = [d for d in drones if d.location == parameters["location"]]
            
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
        
        elif tool_name == "assign_pilot_to_mission":
            mission_id = parameters["mission_id"]
            result = self.assignment_service.assign_mission(mission_id)
            
            if result.success:
                return f"✅ {result.message}\nPilot: {result.assigned_pilot}\nDrone: {result.assigned_drone}"
            else:
                conflicts_str = "\n".join(f"- {c}" for c in result.conflicts)
                return f"❌ {result.message}\n\nConflicts:\n{conflicts_str}"
        
        elif tool_name == "check_mission_conflicts":
            mission_id = parameters["mission_id"]
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
        
        elif tool_name == "update_pilot_status":
            pilot_id = parameters["pilot_id"]
            status = parameters["status"]
            
            success = self.sheets.update_pilot_status(pilot_id, status)
            
            if success:
                return f"✅ Updated pilot {pilot_id} status to {status}"
            else:
                return f"❌ Failed to update pilot {pilot_id}"
        
        elif tool_name == "get_all_missions":
            missions = self.sheets.get_all_missions()
            
            if not missions:
                return "No missions found"
            
            result = "Current Missions:\n"
            for m in missions:
                result += f"\n- {m.client} (ID: {m.project_id})\n"
                result += f"  Location: {m.location}\n"
                result += f"  Dates: {m.start_date.strftime('%Y-%m-%d')} to {m.end_date.strftime('%Y-%m-%d')}\n"
                result += f"  Priority: {m.priority}\n"
                result += f"  Required Skills: {', '.join(m.required_skills)}\n"
            
            return result
        
        else:
            return f"Unknown tool: {tool_name}"