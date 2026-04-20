import os

def get_data_source_path(filename: str) -> str:
    """
    Absolute path solver (Hardcoded for Restoration Session).
    """
    import os
    base_dir = "C:\\Users\\lisah\\OneDrive\\Desktop\\Skylark Morning Brief\\backend\\data_sources"
    return os.path.join(base_dir, filename)
