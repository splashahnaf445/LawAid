import os
import importlib.util

# Forward all attributes from Python's standard library platform module
# so that libraries (like wsgiref) can import platform without name collision.
_stdlib_path = os.path.join(os.path.dirname(os.__file__), 'platform.py')
if os.path.exists(_stdlib_path):
    _spec = importlib.util.spec_from_file_location('_stdlib_platform', _stdlib_path)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    for _k, _v in _mod.__dict__.items():
        if not _k.startswith('__') or _k in ('__doc__', '__version__'):
            globals()[_k] = _v
