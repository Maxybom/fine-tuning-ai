import os
import shutil
import subprocess
import platform

def compile_llama_cpp():
    os_name = platform.system()
    missing_tools = False

    if shutil.which("cmake") is None:
        print("'cmake' not found. Please install it from https://cmake.org/download/")
        missing_tools = True
    else:
        print("CMake detected.")

    if os_name in ("Linux", "Darwin"):
        if shutil.which("make") is None and shutil.which("ninja") is None:
            print("Neither 'make' nor 'ninja' found. Install with: sudo apt install build-essential (Linux) or xcode-select --install (macOS)")
            missing_tools = True
        else:
            print("Make or Ninja detected.")

        if shutil.which("g++") is None and shutil.which("clang++") is None:
            print("No C++ compiler found. Install with: sudo apt install build-essential (Linux) or xcode-select --install (macOS)")
            missing_tools = True
        else:
            print("C++ compiler detected.")

    def get_cmake_generators():
        try:
            result = subprocess.run(["cmake", "--help"], capture_output=True, text=True)
            return result.stdout
        except Exception:
            return ""

    
    def find_generator():
        help_text = get_cmake_generators()
        if os_name == "Windows":
            candidates = [
                "Visual Studio 17 2022",
                "Visual Studio 16 2019",
                "MinGW Makefiles",
                "Ninja"
            ]
        elif os_name == "Darwin":
            candidates = [
                "Xcode",
                "Unix Makefiles",
                "Ninja"
            ]
        else:  # Linux
            candidates = [
                "Unix Makefiles",
                "Ninja"
            ]
        for gen in candidates:
            if gen in help_text:
                return gen
        return None

    if missing_tools:
        print("Missing required tools. Compilation aborted.")
        return False

    llama_root = os.path.abspath("extern/llama.cpp")
    build_dir = os.path.join(llama_root, "build")
    os.makedirs(build_dir, exist_ok=True)

    cache_file = os.path.join(build_dir, "CMakeCache.txt")
    cache_dir = os.path.join(build_dir, "CMakeFiles")
    if os.path.exists(cache_file):
        os.remove(cache_file)
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)

    generator = find_generator()
    if not generator:
        print("No supported CMake generator found. Please install Visual Studio, Make, Ninja, or Xcode.")
        return False

    cmake_cmd = ["cmake", "..", "-G", generator]
    if os_name == "Windows" and "Visual Studio" in generator:
        cmake_cmd += ["-A", "x64", "-DLLAMA_CURL=OFF"]

    # Compile the 'llama-quantize' target in Release mode
    build_cmd = ["cmake", "--build", ".", "--target", "llama-quantize", "--config", "Release"]

    print(f"Using generator: {generator}")
    print("Starting compilation...")
    try:
        subprocess.run(cmake_cmd, cwd=build_dir, check=True)
        subprocess.run(build_cmd, cwd=build_dir, check=True)
        print("Compilation completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Compilation failed: {e}")
        return False
