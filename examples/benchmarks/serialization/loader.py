###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) typedef int GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

"""
Data loader for serialization benchmarks.

Loads vehicle telemetry data from CSV files and creates WAMP message payloads
with various sizes and modes.
"""

import csv
import hashlib
import math
import os
import random
import struct
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

import cbor2

from autobahn.util import utcnow, utcstr

from sample import JSON_DATA1, JSON_DATA2, JSON_DATA3

__all__ = [
    "PAYLOAD_MODE_NORMAL",
    "PAYLOAD_MODE_TRANSPARENT",
    "PAYLOAD_SIZE_EMPTY",
    "PAYLOAD_SIZE_SMALL",
    "PAYLOAD_SIZE_MEDIUM",
    "PAYLOAD_SIZE_LARGE",
    "PAYLOAD_SIZE_XL",
    "PAYLOAD_SIZE_XXL",
    "VehicleEvent",
    "load",
]

# Payload modes
PAYLOAD_MODE_NORMAL = "normal"
PAYLOAD_MODE_TRANSPARENT = "transparent"

# Payload sizes
PAYLOAD_SIZE_EMPTY = "empty"
PAYLOAD_SIZE_SMALL = "small"
PAYLOAD_SIZE_MEDIUM = "medium"
PAYLOAD_SIZE_LARGE = "large"
PAYLOAD_SIZE_XL = "xl"
PAYLOAD_SIZE_XXL = "xxl"


def deg2num(lat_deg: float, lon_deg: float, zoom: int) -> Tuple[int, int]:
    """
    Convert latitude/longitude to tile coordinates.

    Args:
        lat_deg: Latitude in degrees
        lon_deg: Longitude in degrees
        zoom: Zoom level

    Returns:
        Tuple of (xtile, ytile) coordinates
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0**zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int(
        (1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi)
        / 2.0
        * n
    )
    return (xtile, ytile)


class VehicleEvent:
    """
    Vehicle telemetry event with configurable payload size.

    Attributes:
        vehicle_id: Vehicle identifier
        timestamp: Event timestamp
        lng: Longitude
        lat: Latitude
        xtile: X tile coordinate
        ytile: Y tile coordinate
        speed: Vehicle speed
        rain: Rain sensor value
        wiper: Wiper status
        pothole_depth: Pothole depth sensor
        pothole_type: Pothole type classification
    """

    def __init__(
        self,
        fleet: Optional[str] = None,
        zoom: int = 18,
        size: str = PAYLOAD_SIZE_SMALL,
    ):
        self._fleet = fleet
        self._zoom = zoom
        self._size = size

        self.vehicle_id = "unknown"
        self.timestamp: Optional[datetime] = None
        self.lng: Optional[float] = None
        self.lat: Optional[float] = None
        self.xtile = 0
        self.ytile = 0
        self.speed: Optional[float] = None
        self.rain: Optional[float] = None
        self.wiper: Optional[str] = None
        self.pothole_depth: Optional[float] = None
        self.pothole_type: Optional[str] = None

        # Pre-generate binary frame data for xl/xxl payloads to avoid memory exhaustion
        # Generating 128KB × 42K events repeatedly would create ~5.5GB per iteration
        self._frame_data: Optional[bytes] = None
        if self._size == PAYLOAD_SIZE_XL:
            self._frame_data = os.urandom(16 * 1024)  # 16KB binary frame
        elif self._size == PAYLOAD_SIZE_XXL:
            self._frame_data = os.urandom(128 * 1024)  # 128KB binary frame

    @staticmethod
    def from_row(row: Dict[str, str], fleet: str, size: str) -> "VehicleEvent":
        """
        Create VehicleEvent from CSV row.

        Args:
            row: CSV row as dictionary
            fleet: Fleet identifier
            size: Payload size (empty, small, medium, large, xl, xxl)

        Returns:
            VehicleEvent instance
        """
        obj = VehicleEvent(fleet=fleet, size=size)
        if size == PAYLOAD_SIZE_EMPTY:
            return obj

        obj.vehicle_id = f"vehicle{row['vehicleID']}"
        obj.timestamp = datetime.strptime(row["ts"], "%Y-%m-%d %H:%M:%S")
        obj.lng = float(row["lon"])
        obj.lat = float(row["lat"])
        if obj.lng and obj.lat:
            obj.xtile, obj.ytile = deg2num(obj.lat, obj.lng, obj._zoom)
        obj.speed = float(row["speed"])

        # Available only in some files
        obj.rain = float(row["rain"])
        obj.wiper = str(row["dyn_wiper"])

        # Use pseudo-random but deterministic value based on vehicle_id and timestamp
        random_in = hashlib.sha256(
            f"{obj.vehicle_id}:{obj.timestamp}".encode()
        ).digest()
        obj.pothole_depth = float(struct.unpack(">L", random_in[:4])[0]) / 2**32
        obj.pothole_type = random.choice(
            ["type-a", "type-b", "type-c", "type-d", "type-e", "type-f"]
        )

        return obj

    def marshal(self) -> Optional[Dict[str, Any]]:
        """
        Marshal event to dictionary for serialization.

        Returns:
            Dictionary representation or None for empty payload
        """
        if self._size == PAYLOAD_SIZE_EMPTY:
            return None

        obj: Dict[str, Any] = {
            "ts": utcnow(),
            "vehicle_id": self.vehicle_id,
            "timestamp": utcstr(self.timestamp),
            "gps_location": {
                "lng": self.lng,
                "lat": self.lat,
                "speed": self.speed,
                "xtile": self.xtile,
                "ytile": self.ytile,
                "zoom": self._zoom,
            },
            "rain_sensor": {
                "rain": self.rain,
                "wiper": self.wiper,
            },
            "pothole_sensor": {
                "depth": self.pothole_depth,
                "type": self.pothole_type,
            },
        }

        # Add additional data for larger payloads
        if self._size in [PAYLOAD_SIZE_MEDIUM, PAYLOAD_SIZE_LARGE]:
            obj.update(JSON_DATA1)

        if self._size == PAYLOAD_SIZE_LARGE:
            obj.update(JSON_DATA2)
            obj.update(JSON_DATA3)

        # Use cached frame data for xl/xxl payloads (pre-generated in __init__)
        if self._frame_data is not None:
            obj["frame"] = self._frame_data

        return obj


def load_dataset(
    files: Dict[str, Tuple[Callable, str]], payload_mode: str, payload_size: str
) -> Tuple[Optional[VehicleEvent], Dict[str, List[Tuple[str, Any]]]]:
    """
    Load vehicle telemetry dataset from CSV files.

    Args:
        files: Mapping of filename to (factory_func, fleet_id)
        payload_mode: 'normal' or 'transparent'
        payload_size: Size category (empty, small, medium, large, xl, xxl)

    Returns:
        Tuple of (sample_event, vehicles_dict)
        where vehicles_dict maps vehicle_id to list of (topic, payload) tuples
    """
    # Limit events for xl/xxl payloads to prevent memory exhaustion
    # xl: 16KB per event → limit to 1000 events (~16MB)
    # xxl: 128KB per event → limit to 100 events (~12.8MB)
    event_limits = {
        PAYLOAD_SIZE_XL: 1000,
        PAYLOAD_SIZE_XXL: 100,
    }
    max_events = event_limits.get(payload_size, None)

    data: Dict[str, List[Tuple[str, Any]]] = {}
    sample: Optional[VehicleEvent] = None

    for filename, (from_row, fleet) in files.items():
        fn = os.path.abspath(os.path.join(os.path.dirname(__file__), filename))
        vehicles: Dict[str, List[Tuple[str, Any]]] = {}

        with open(fn, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            # Limit events for large payloads to prevent memory issues
            if max_events:
                vehicle_events = [
                    from_row(row, fleet, size=payload_size)
                    for i, row in enumerate(reader)
                    if i < max_events
                ]
            else:
                vehicle_events = [
                    from_row(row, fleet, size=payload_size) for row in reader
                ]

        for evt in vehicle_events:
            if not sample:
                sample = evt

            vehicle_id = f"{fleet}-{evt.vehicle_id}"
            topic = f"com.example.vehicle.{evt.vehicle_id}.xtile.{evt.xtile}.ytile.{evt.ytile}"

            if payload_mode == PAYLOAD_MODE_NORMAL:
                evt_data = evt.marshal() if payload_size != PAYLOAD_SIZE_EMPTY else None
            elif payload_mode == PAYLOAD_MODE_TRANSPARENT:
                if payload_size == PAYLOAD_SIZE_EMPTY:
                    evt_data = b""
                else:
                    evt_data = cbor2.dumps(evt.marshal())
            else:
                raise NotImplementedError(f'invalid payload_mode "{payload_mode}"')

            if vehicle_id not in vehicles:
                vehicles[vehicle_id] = []

            vehicles[vehicle_id].append((topic, evt_data))

        data.update(vehicles)

    return sample, data


def load(
    payload_mode: str = PAYLOAD_MODE_NORMAL, payload_size: str = PAYLOAD_SIZE_SMALL
) -> Tuple[Optional[VehicleEvent], Dict[str, List[Tuple[str, Any]]]]:
    """
    Load default vehicle telemetry datasets.

    Args:
        payload_mode: 'normal' (WAMP args) or 'transparent' (WAMP payload)
        payload_size: Size category (empty, small, medium, large, xl, xxl)

    Returns:
        Tuple of (sample_event, vehicles_dict)
    """
    files = {
        "data/dataset1.csv": (VehicleEvent.from_row, "fleet1"),
        "data/dataset2.csv": (VehicleEvent.from_row, "fleet2"),
    }
    return load_dataset(files, payload_mode=payload_mode, payload_size=payload_size)


if __name__ == "__main__":
    sample_evt, vehicles = load()
    print(f"Ok, data loaded from {len(vehicles)} vehicles:")
    for vehicle in vehicles:
        cnt = len(vehicles[vehicle])
        print(f"{vehicle}: {cnt} events")
