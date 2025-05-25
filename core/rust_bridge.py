import ctypes
import os
import platform

def load_rust_lib():
    if platform.system() == "Windows":
        libname = "aegis_core.dll"
    else:
        libname = "libaegis_core.so"
    path = os.path.join(os.path.dirname(__file__), libname)
    return ctypes.CDLL(path)

lib = load_rust_lib()
lib.calculate_risk.argtypes = [ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
lib.calculate_risk.restype = ctypes.c_uint8

def get_risk_score(cpu, ram, net):
    return lib.calculate_risk(cpu, ram, net)