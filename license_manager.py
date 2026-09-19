import json
import os
import uuid
import hashlib
from datetime import datetime, timedelta

APP_NAME = "GREENBIBLE"
TRIAL_DAYS = 14

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LICENSE_FILE = os.path.join(BASE_DIR, "greenbible_license.json")


def _machine_id():
    raw = f"{os.environ.get('COMPUTERNAME', '')}|{uuid.getnode()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _today():
    return datetime.now().date()


def _load():
    if not os.path.exists(LICENSE_FILE):
        return {}

    try:
        with open(LICENSE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save(data):
    with open(LICENSE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def start_trial():
    data = _load()

    if "trial_start" not in data:
        data["trial_start"] = _today().isoformat()
        data["machine_id"] = _machine_id()
        _save(data)

    return trial_status()


def trial_status():
    data = _load()

    if "trial_start" not in data:
        start_trial()
        data = _load()

    try:
        start = datetime.strptime(
            data["trial_start"], "%Y-%m-%d"
        ).date()
    except Exception:
        return {
            "active": False,
            "days_left": 0,
            "message": "Trial information is invalid."
        }

    elapsed = (_today() - start).days
    days_left = max(0, TRIAL_DAYS - elapsed)

    return {
        "active": elapsed < TRIAL_DAYS,
        "days_left": days_left,
        "message": (
            f"{days_left} day(s) remaining in your GREENBIBLE trial."
            if days_left > 0
            else "Your GREENBIBLE trial has expired."
        )
    }


def activate_license(license_key, customer_email=""):
    license_key = str(license_key).strip()

    if not license_key:
        return {
            "success": False,
            "message": "Please enter a license key."
        }

    data = _load()

    # V1.1 development activation.
    # Online verification will be connected in the next stage.
    data["license_key"] = license_key
    data["customer_email"] = str(customer_email).strip()
    data["machine_id"] = _machine_id()
    data["activated_at"] = datetime.now().isoformat()
    data["status"] = "active"

    _save(data)

    return {
        "success": True,
        "message": "GREENBIBLE has been activated on this computer."
    }


def deactivate_license():
    data = _load()

    if not data:
        return {
            "success": False,
            "message": "No license information found."
        }

    data.pop("license_key", None)
    data.pop("customer_email", None)
    data.pop("activated_at", None)
    data["status"] = "trial"

    _save(data)

    return {
        "success": True,
        "message": "GREENBIBLE license has been deactivated."
    }


def get_license_status():
    data = _load()

    if data.get("status") == "active" and data.get("license_key"):
        return {
            "licensed": True,
            "status": "Active",
            "customer_email": data.get("customer_email", ""),
            "license_key": data.get("license_key", ""),
            "machine_id": data.get("machine_id", ""),
            "message": "GREENBIBLE is activated."
        }

    trial = trial_status()

    return {
        "licensed": False,
        "status": "Trial",
        "customer_email": "",
        "license_key": "",
        "machine_id": _machine_id(),
        "trial_active": trial["active"],
        "days_left": trial["days_left"],
        "message": trial["message"]
    }


def is_licensed():
    status = get_license_status()
    return status.get("licensed", False)


def can_use():
    status = get_license_status()

    if status.get("licensed"):
        return True

    return status.get("trial_active", False)