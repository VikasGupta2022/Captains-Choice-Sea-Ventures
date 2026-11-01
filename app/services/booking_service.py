import json
import random
import string
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import BASE_DIR

CATALOG_PATH = BASE_DIR / "app" / "data" / "fleet_catalog.json"

class BookingService:
    def __init__(self):
        self._catalog_cache: Optional[Dict[str, Any]] = None
        self._load_catalog()

    def _load_catalog(self) -> Dict[str, Any]:
        """Load fleet catalog from JSON data file (or reload if changed)"""
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            self._catalog_cache = json.load(f)
        return self._catalog_cache

    def get_catalog(self) -> Dict[str, Any]:
        return self._load_catalog()

    def get_routes(self) -> List[Dict[str, Any]]:
        return self.get_catalog().get("routes", [])

    def get_route_by_id(self, route_id: str) -> Optional[Dict[str, Any]]:
        for r in self.get_routes():
            if r["id"] == route_id:
                return r
        return None

    def get_fleet(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        boats = self.get_catalog().get("boats", [])
        if category and category.lower() != "all":
            return [b for b in boats if b["category"].lower() == category.lower()]
        return boats

    def get_boat_by_id(self, boat_id: str) -> Optional[Dict[str, Any]]:
        for b in self.get_catalog().get("boats", []):
            if b["id"] == boat_id:
                return b
        return None

    def get_addons(self) -> List[Dict[str, Any]]:
        return self.get_catalog().get("addons", [])

    def get_time_slots(self) -> List[str]:
        return self.get_catalog().get("time_slots", [])

    def calculate_fare(
        self,
        boat_id: str,
        route_id: str,
        trip_type: str = "one_way",
        passengers: int = 1,
        addon_ids: List[str] = None
    ) -> Dict[str, Any]:
        boat = self.get_boat_by_id(boat_id)
        if not boat:
            raise ValueError(f"Boat '{boat_id}' not found.")
        
        route = self.get_route_by_id(route_id)
        if not route:
            raise ValueError(f"Route '{route_id}' not found.")

        # Determine route-specific base price from boat
        if "mandwa" in route_id:
            base_price = boat.get("price_gateway_mandwa", 6500)
        elif "elephanta" in route_id:
            base_price = boat.get("price_elephanta", 7500)
        elif "cruise" in route_id or "harbour" in route_id:
            base_price = boat.get("price_harbour_cruise", 4500)
        else:
            base_price = route.get("base_fare", 6500)

        # Multiplier based on trip type
        if trip_type == "round_trip":
            # 10% round trip package discount
            multiplier = 1.90
        elif trip_type == "harbour_cruise":
            multiplier = 1.0
        else:
            multiplier = 1.0

        trip_fare = round(base_price * multiplier)

        # Add-ons calculation
        addons_total = 0
        all_addons = {a["id"]: a for a in self.get_addons()}
        selected_addons_detail = []
        if addon_ids:
            for aid in addon_ids:
                if aid in all_addons:
                    addons_total += all_addons[aid]["price"]
                    selected_addons_detail.append(all_addons[aid])

        total_fare = trip_fare + addons_total
        
        # Advance required: default to boat's configured advance deposit or 30% of total
        boat_advance = boat.get("advance_deposit", 2000)
        if trip_type == "round_trip":
            advance_required = min(total_fare, boat_advance * 2)
        else:
            advance_required = min(total_fare, boat_advance)

        balance_due = max(0, total_fare - advance_required)

        return {
            "boat_id": boat["id"],
            "boat_name": boat["name"],
            "boat_image": boat["image"],
            "route_id": route["id"],
            "route_name": route["name"],
            "trip_type": trip_type,
            "passengers": passengers,
            "base_fare": base_price,
            "trip_multiplier": multiplier,
            "addons_fare": addons_total,
            "selected_addons": selected_addons_detail,
            "total_fare": total_fare,
            "advance_required": advance_required,
            "balance_due": balance_due,
            "currency": "INR"
        }

    def generate_booking_ref(self) -> str:
        """Create a clean human-readable booking reference e.g. GSB-20261101-7F2A"""
        today_str = datetime.date.today().strftime("%Y%m%d")
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"GSB-{today_str}-{suffix}"

booking_service = BookingService()
