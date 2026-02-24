import os
import sys
import subprocess
import platform

os.environ["CUDA_VISIBLE_DEVICES"] = ""

MODEL_NAME = "model"
QUANTIZATION_TYPE = "Q4_K_M"
MODEL_INPUT_DIR = "./merged-model"
OUTPUT_DIR = "./gguf-output"

try:
    from compile_llama_cpp import compile_llama_cpp
    if not compile_llama_cpp():
        print("Compilation failed or skipped.")
except ImportError:
    print("compile_llama_cpp module not found.")

llama_root = os.path.abspath("extern/llama.cpp")
converter_script = os.path.join(llama_root, "convert_hf_to_gguf.py")

is_windows = platform.system() == "Windows"
bin_name = "llama-quantize.exe" if is_windows else "llama-quantize"
build_bin_path = os.path.join(llama_root, "build", "bin")

# Binary
possible_paths = [
    os.path.join(build_bin_path, "Release", bin_name),
    os.path.join(build_bin_path, bin_name),
    os.path.join(llama_root, "build", bin_name)
]

quantizer_bin = None
for path in possible_paths:
    if os.path.exists(path):
        quantizer_bin = path
        print(f"Quantizer found at: {quantizer_bin}")
        break

if not quantizer_bin:
    print(f"Error: {bin_name} not found. Searched in: {possible_paths}")
    sys.exit(1)
# --------------------------------------------

model_dir = os.path.abspath(MODEL_INPUT_DIR)
output_dir = os.path.abspath(OUTPUT_DIR)
os.makedirs(output_dir, exist_ok=True)

f16_file = os.path.join(output_dir, f"{MODEL_NAME}-f16.gguf")

print(f"Starting F16 conversion on {platform.system()}...")
subprocess.run([
    sys.executable, converter_script,
    model_dir,
    "--outfile", f16_file,
    "--outtype", "f16"
], check=True)

print(f"Starting {QUANTIZATION_TYPE} quantization...")
quantized_filename = f"{MODEL_NAME}-{QUANTIZATION_TYPE.lower()}.gguf"
q4_file = os.path.join(output_dir, quantized_filename)

subprocess.run([
    quantizer_bin, 
    f16_file, 
    q4_file, 
    QUANTIZATION_TYPE
], check=True)

print(f"Quantization completed successfully: {q4_file}")