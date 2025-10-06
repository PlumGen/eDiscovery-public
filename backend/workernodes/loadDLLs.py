import sys
import os
import platform
import site

def add_dll_directories_from_site_packages():
    if platform.system() == "Windows":
        for p in site.getsitepackages():
            if os.path.isdir(p):
                for root, dirs, files in os.walk(p):
                    if any(f.lower().endswith(".dll") for f in files):
                        try:
                            os.add_dll_directory(root)
                        except Exception:
                            pass
    elif platform.system() == "Linux":
        ld_paths = []

        # Add Conda environment's lib directory dynamically
        conda_prefix = os.environ.get("CONDA_PREFIX")
        if conda_prefix:
            lib_path = os.path.join(conda_prefix, "lib")
            if os.path.isdir(lib_path):
                ld_paths.append(lib_path)

        # Add site-packages paths as fallback
        for p in site.getsitepackages():
            if os.path.isdir(p):
                ld_paths.append(p)

        os.environ["LD_LIBRARY_PATH"] = ":".join(ld_paths) + ":" + os.environ.get("LD_LIBRARY_PATH", "")
    
    return True