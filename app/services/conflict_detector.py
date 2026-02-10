from typing import List, Tuple
from datetime import datetime
from app.models import Pilot, Drone, Mission, ConflictCheck


class ConflictDetector:

    def check_pilot_availability(
            self,
            pilot: Pilot,
            mission: Mission
    ) -> ConflictCheck:
        """Check if pilot is available for mission"""
        conflicts = []
        
        # Check status
        if pilot.status != "available":
            conflicts.append(f"Pilot {pilot.name} is currently {pilot.status}")
        
        # Check availability date
        if pilot.available_from and mission.start_date:
            if pilot.available_from > mission.start_date:
                conflicts.append(
                    f"Pilot not available until {pilot.available_from.strftime('%Y-%m-%d')}"
                )
        
        # Check location
        if pilot.location != mission.location:
            conflicts.append(
                f"Location mismatch: Pilot in {pilot.location}, mission in {mission.location}"
            )
        
        # Check skills
        missing_skills = set(mission.required_skills) - set(pilot.skills)
        if missing_skills:
            conflicts.append(f"Missing skills: {', '.join(missing_skills)}")
        
        # Check certifications
        missing_certs = set(mission.required_certs) - set(pilot.certifications)
        if missing_certs:
            conflicts.append(f"Missing certifications: {', '.join(missing_certs)}")
        
        return ConflictCheck(
            has_conflict=len(conflicts) > 0,
            conflict_type="pilot_availability" if conflicts else None,
            details=conflicts
        )
    
    def check_drone_availability(
            self, 
            drone: Drone, 
            mission: Mission
        ) -> ConflictCheck:
        """Check if drone is available for mission"""
        conflicts = []
        
        # Check status
        if drone.status != "available":
            conflicts.append(f"Drone {drone.drone_id} is currently {drone.status}")
        
        # Check maintenance
        if drone.maintenance_due and mission.start_date:
            if drone.maintenance_due <= mission.start_date:
                conflicts.append(
                    f"Maintenance due before mission start: {drone.maintenance_due.strftime('%Y-%m-%d')}"
                )
        
        # Check location
        if drone.location != mission.location:
            conflicts.append(
                f"Location mismatch: Drone in {drone.location}, mission in {mission.location}"
            )
        
        return ConflictCheck(
            has_conflict=len(conflicts) > 0,
            conflict_type="drone_availability" if conflicts else None,
            details=conflicts
        )
    
    def check_date_overlap(
        self,
        existing_missions: List[Mission],
        new_mission: Mission,
        pilot_id: str
    ) -> ConflictCheck:
        """Check for date overlaps in pilot assignments"""
        conflicts = []
        
        for mission in existing_missions:
            # Check if this pilot is assigned to this mission
            # (You'd need to track this in your sheets or separately)
            
            # Check date overlap
            if mission.start_date and mission.end_date and new_mission.start_date and new_mission.end_date:
                if (new_mission.start_date <= mission.end_date and 
                    new_mission.end_date >= mission.start_date):
                    conflicts.append(
                        f"Date overlap with mission {mission.project_id} "
                        f"({mission.start_date.strftime('%Y-%m-%d')} to {mission.end_date.strftime('%Y-%m-%d')})"
                    )
        
        return ConflictCheck(
            has_conflict=len(conflicts) > 0,
            conflict_type="date_overlap" if conflicts else None,
            details=conflicts
        )