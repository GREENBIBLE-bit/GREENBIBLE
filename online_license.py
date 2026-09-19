import requests

# GREENBIBLE V1.1 — Online License Verification Foundation
#
# This file is intentionally separate from license_manager.py.
# The real Lemon Squeezy API connection will be configured in the
# next licensing stage.

APP_NAME = "GREENBIBLE"

# Placeholder until the Lemon Squeezy store/license configuration
# is created.
LICENSE_API_URL = ""


def verify_online(license_key, instance_id=None):
    """
    Verify a GREENBIBLE license online.

    Returns a consistent result structure so the main application
    can use it later without changing the interface.
    """

    license_key = str(license_key).strip()

    if not license_key:
        return {
            "success": False,
            "status": "invalid",
            "message": "Please enter a license key."
        }

    if not LICENSE_API_URL:
        return {
            "success": False,
            "status": "not_configured",
            "message": "Online license verification is not configured yet."
        }

    try:
        payload = {
            "license_key": license_key
        }

        if instance_id:
            payload["instance_id"] = instance_id

        response = requests.post(
            LICENSE_API_URL,
            json=payload,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        return {
            "success": bool(data.get("success")),
            "status": data.get("status", "unknown"),
            "message": data.get(
                "message",
                "License verification completed."
            ),
            "data": data
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "status": "network_error",
            "message": f"Unable to verify license online: {e}"
        }

    except ValueError:
        return {
            "success": False,
            "status": "invalid_response",
            "message": "The license server returned an invalid response."
        }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "message": f"License verification error: {e}"
        }