import os
import shutil
import subprocess
import platform
import sys

def compile_llama_cpp():
    os_name = platform.system()
    missing_tools = False

    print(f"--- Checking tools for OS: {os_name} ---")

    if shutil.which("cmake") is None:
        print("ERROR: 'cmake' not found. Please install it.")
        missing_tools = True
    else:
        print("[OK] CMake detected.")

    if os_name in ("Linux", "Darwin"):
        if shutil.which("make") is None and shutil.which("ninja") is None:
            print("ERROR: Neither 'make' nor 'ninja' found.")
            missing_tools = True
        else:
            print("[OK] Build tools detected.")

        if shutil.which("g++") is None and shutil.which("clang++") is None:
            print("ERROR: No C++ compiler found.")
            missing_tools = True
        else:
            print("[OK] C++ compiler detected.")

    if missing_tools:
        return False

    cwd = os.getcwd()
    llama_root = os.path.join(cwd, "extern", "llama.cpp")
    build_dir = os.path.join(llama_root, "build")
    
    if not os.path.exists(llama_root):
        print(f"ERROR: llama.cpp not found at: {llama_root}")
        return False

    os.makedirs(build_dir, exist_ok=True)

    def find_generator():
        try:
            help_text = subprocess.run(["cmake", "--help"], capture_output=True, text=True).stdout
        except:
            return None
            
        if os_name == "Windows":
            candidates = ["Visual Studio 17 2022", "Visual Studio 16 2019", "MinGW Makefiles", "Ninja"]
        else:
            candidates = ["Unix Makefiles", "Ninja", "Xcode"]
            
        for gen in candidates:
            if gen in help_text:
                return gen
        return None

    generator = find_generator()
    if not generator:
        print("ERROR: No CMake generator found.")
        return False

    print(f"Using generator: {generator}")
    base_cmd = ["cmake", "..", "-G", generator, "-DCMAKE_BUILD_TYPE=Release"]

    if os_name == "Windows" and "Visual Studio" in generator:
        base_cmd += ["-A", "x64"]

    print("\n--- Configuration ---")
    try:
        subprocess.run(base_cmd, cwd=build_dir, check=True)
    except subprocess.CalledProcessError:
        print("Attempting Offline Mode...")
        shutil.rmtree(os.path.join(build_dir, "CMakeFiles"), ignore_errors=True)
        if os.path.exists(os.path.join(build_dir, "CMakeCache.txt")):
            os.remove(os.path.join(build_dir, "CMakeCache.txt"))
        
        try:
            subprocess.run(base_cmd + ["-DLLAMA_CURL=OFF"], cwd=build_dir, check=True)
        except subprocess.CalledProcessError:
            return False

    print("\n--- Build ---")
    build_cmd = ["cmake", "--build", ".", "--target", "llama-quantize", "--config", "Release", "-j", "4"]
    try:
        subprocess.run(build_cmd, cwd=build_dir, check=True)
        print("\n" + "="*30)
        print(" BUILD SUCCESSFUL ")
        print("="*30 + "\n")
        return True
    except subprocess.CalledProcessError:
        return False

if __name__ == "__main__":
    compile_llama_cpp()