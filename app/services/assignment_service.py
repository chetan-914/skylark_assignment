from typing import Optional, List, Tuple
from app.models import Pilot, Drone, Mission, AssignmentResult, Priority
from app.services.sheets_services import SheetsService
from app.services.conflict_detector import ConflictDetector


class AssignmentService:
    def __init__(self):
        self.sheets = SheetsService()
        self.conflict_detector = ConflictDetector()
    
    def find_best_pilot(
        self, 
        mission: Mission,
        pilots: Optional[List[Pilot]] = None
    ) -> Tuple[Optional[Pilot], List[str]]:
        """Find best pilot for mission"""
        if pilots is None:
            pilots = self.sheets.get_all_pilots()
        
        candidates = []
        all_issues = []
        
        for pilot in pilots:
            conflict_check = self.conflict_detector.check_pilot_availability(pilot, mission)
            
            if not conflict_check.has_conflict:
                # Calculate score
                score = 0
                # Exact location match
                if pilot.location == mission.location:
                    score += 10
                # Skills match
                skill_match = len(set(pilot.skills) & set(mission.required_skills))
                score += skill_match * 5
                # Certification match
                cert_match = len(set(pilot.certifications) & set(mission.required_certs))
                score += cert_match * 5
                
                candidates.append((pilot, score))
            else:
                all_issues.extend(conflict_check.details)
        
        if candidates:
            # Sort by score
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0], []
        
        return None, all_issues
    
    def find_best_drone(
        self,
        mission: Mission,
        drones: Optional[List[Drone]] = None
    ) -> Tuple[Optional[Drone], List[str]]:
        """Find best drone for mission"""
        if drones is None:
            drones = self.sheets.get_all_drones()
        
        candidates = []
        all_issues = []
        
        for drone in drones:
            conflict_check = self.conflict_detector.check_drone_availability(drone, mission)
            
            if not conflict_check.has_conflict:
                # Calculate score
                score = 0
                # Exact location match
                if drone.location == mission.location:
                    score += 10
                # Capability count
                score += len(drone.capabilities) * 2
                
                candidates.append((drone, score))
            else:
                all_issues.extend(conflict_check.details)
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0], []
        
        return None, all_issues
    
    def assign_mission(self, mission_id: str) -> AssignmentResult:
        """Assign pilot and drone to mission"""
        mission = self.sheets.get_mission_by_id(mission_id)
        
        if not mission:
            return AssignmentResult(
                success=False,
                message=f"Mission {mission_id} not found"
            )
        
        # Find best pilot
        pilot, pilot_issues = self.find_best_pilot(mission)
        
        # Find best drone
        drone, drone_issues = self.find_best_drone(mission)
        
        if not pilot:
            return AssignmentResult(
                success=False,
                message="No suitable pilot found",
                conflicts=pilot_issues
            )
        
        if not drone:
            return AssignmentResult(
                success=False,
                message="No suitable drone found",
                conflicts=drone_issues
            )
        
        # Update sheets
        pilot_updated = self.sheets.update_pilot_status(
            pilot.pilot_id, 
            "assigned", 
            mission_id
        )
        
        drone_updated = self.sheets.update_drone_status(
            drone.drone_id,
            "in_use",
            mission_id
        )
        
        if pilot_updated and drone_updated:
            return AssignmentResult(
                success=True,
                message=f"Successfully assigned {pilot.name} and {drone.drone_id} to mission {mission_id}",
                assigned_pilot=pilot.name,
                assigned_drone=drone.drone_id
            )
        else:
            return AssignmentResult(
                success=False,
                message="Failed to update sheets",
                conflicts=["Sheet update failed"]
            )