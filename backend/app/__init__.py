"""
Healthcare Auditor FastAPI Application.
"""

def get_app():
    from .main import app
    return app

__all__ = ["get_app"]
