import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Optional
from datetime import datetime
from app.config import get_settings
from app.models import Pilot, Drone, Mission, PilotStatus, DroneStatus, Priority

class SheetsService:
    def __init__(self):
        settings = get_settings()

        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = Credentials.from_service_account_file(
            settings.google_sheets_credentials_path,
            scopes=scopes
        )

        self.client = gspread.authorize(creds)

        self.pilot_sheet = self.client.open_by_key(settings.pilot_roster_sheet_id).sheet1
        self.drone_sheet = self.client.open_by_key(settings.drone_fleet_sheet_id).sheet1
        self.mission_sheet = self.client.open_by_key(settings.mission_sheet_id).sheet1

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime"""
        if not date_str or date_str == "":
            return None
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return None
        
    def _parse_list(self, list_str: str) -> List[str]:
        """Parse comma-separated string to list"""
        if not list_str or list_str == "":
            return []
        return [item.strip() for item in list_str.split(",")]
    
    # PILOTS
    def get_all_pilots(self) -> List[Pilot]:
        """Fetch all pilots from Google Sheets"""
        records = self.pilot_sheet.get_all_records()
        pilots = []
        
        for row in records:
            try:
                pilot = Pilot(
                    pilot_id=str(row.get('pilot_id', '')),
                    name=row.get('name', ''),
                    skills=self._parse_list(row.get('skills', '')),
                    certifications=self._parse_list(row.get('certifications', '')),
                    location=row.get('location', ''),
                    status=PilotStatus(row.get('status', '')),
                    current_assignment=row.get('current_assignment') or None,
                    available_from=self._parse_date(row.get('available_from', ''))
                )
                pilots.append(pilot)
            except Exception as e:
                print(f"Error parsing pilot row: {e}")
                continue
        
        return pilots
    
    def update_pilot_status(self, pilot_id: str, status: str, assignment: Optional[str] = None) -> bool:
        """Update pilot status in Google Sheets"""
        try:
            cell = self.pilot_sheet.find(pilot_id)
            if cell:
                row = cell.row
                # Update status (column 6)
                self.pilot_sheet.update_cell(row, 6, status)
                # Update assignment (column 7)
                if assignment is not None:
                    self.pilot_sheet.update_cell(row, 7, assignment)
                return True
        except Exception as e:
            print(f"Error updating pilot: {e}")
        return False
    
    # DRONES
    def get_all_drones(self) -> List[Drone]:
        """Fetch all drones from Google Sheets"""
        records = self.drone_sheet.get_all_records()
        drones = []
        
        for row in records:
            try:
                drone = Drone(
                    drone_id=str(row.get('drone_id', '')),
                    model=row.get('model', ''),
                    capabilities=self._parse_list(row.get('capabilities', '')),
                    status=DroneStatus(row.get('status', '')),
                    location=row.get('location', ''),
                    current_assignment=row.get('current_assignment') or None,
                    maintenance_due=self._parse_date(row.get('maintenance_due', ''))
                )
                drones.append(drone)
            except Exception as e:
                print(f"Error parsing drone row: {e}")
                continue
        
        return drones
    
    def update_drone_status(self, drone_id: str, status: str, assignment: Optional[str] = None) -> bool:
        """Update drone status in Google Sheets"""
        try:
            cell = self.drone_sheet.find(drone_id)
            if cell:
                row = cell.row
                # Update status (column 4)
                self.drone_sheet.update_cell(row, 4, status)
                # Update assignment (column 6)
                if assignment is not None:
                    self.drone_sheet.update_cell(row, 6, assignment)
                return True
        except Exception as e:
            print(f"Error updating drone: {e}")
        return False
    
    # MISSIONS
    def get_all_missions(self) -> List[Mission]:
        """Fetch all missions from Google Sheets"""
        records = self.mission_sheet.get_all_records()
        missions = []
        
        for row in records:
            try:
                mission = Mission(
                    project_id=str(row.get('project_id', '')),
                    client=row.get('client', ''),
                    location=row.get('location', ''),
                    required_skills=self._parse_list(row.get('required_skills', '')),
                    required_certs=self._parse_list(row.get('required_certs', '')),
                    start_date=self._parse_date(row.get('start_date', '')),
                    end_date=self._parse_date(row.get('end_date', '')),
                    priority=Priority(row.get('priority', 'medium'))
                )
                missions.append(mission)
            except Exception as e:
                print(f"Error parsing mission row: {e}")
                continue
        
        return missions
    
    def get_mission_by_id(self, project_id: str) -> Optional[Mission]:
        """Get specific mission by ID"""
        missions = self.get_all_missions()
        for mission in missions:
            if mission.project_id == project_id:
                return mission
        return None