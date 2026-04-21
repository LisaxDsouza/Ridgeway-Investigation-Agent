import os

def get_data_source_path(filename: str) -> str:
    """
    Absolute path solver that works across both local and cloud (Linux) environments.
    """
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # The data_sources directory is at backend/data_sources, which is two levels up from this file
    # (app/mcp_server/utils.py -> app/mcp_server -> app -> backend)
    # Actually mcp_server is inside app, and app is inside backend.
    # So it's: backend/app/mcp_server/utils.py
    # data_sources is in backend/data_sources
    base_dir = os.path.join(current_dir, "..", "..", "data_sources")
    return os.path.normpath(os.path.join(base_dir, filename))
