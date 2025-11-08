import os
import sys
import subprocess
import platform
from compile_llama_cpp import compile_llama_cpp 

MODEL_NAME = "model"                    
QUANTIZATION_TYPE = "Q4_K_M"           
QUANTIZATION_GROUP_SIZE = "8"           
MODEL_INPUT_DIR = "./merged-model"     
OUTPUT_DIR = "./gguf-output"            

if not compile_llama_cpp():
    print("Compilation step failed or skipped. Continuing with conversion/quantization if possible.")

llama_root = os.path.abspath("extern/llama.cpp")
converter_script = os.path.join(llama_root, "convert_hf_to_gguf.py")
quantizer_bin = os.path.join(llama_root, "build", "bin", "Release", "llama-quantize.exe" if platform.system() == "Windows" else "llama-quantize")

if not os.path.exists(converter_script):
    print(f"Conversion script not found: {converter_script}")
if not os.path.exists(quantizer_bin):
    print(f"Quantization binary not found: {quantizer_bin}")

model_dir = os.path.abspath(MODEL_INPUT_DIR)
output_dir = os.path.abspath(OUTPUT_DIR)
os.makedirs(output_dir, exist_ok=True)

if not os.path.exists(model_dir):
    print(f"Model folder not found: {model_dir}")

# Convert to F16
f16_file = os.path.join(output_dir, f"{MODEL_NAME}-f16.gguf")
convert_cmd = [
    sys.executable, converter_script,
    model_dir,
    "--outfile", f16_file,
    "--outtype", "f16",
    "--verbose"
]

if os.path.exists(converter_script) and os.path.exists(model_dir):
    print("Starting F16 conversion...")
    try:
        convert_proc = subprocess.Popen(convert_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                        text=True, encoding="utf-8", errors="replace")
        for line in convert_proc.stdout:
            print(line, end="")
        convert_proc.wait()
        if convert_proc.returncode == 0 and os.path.exists(f16_file):
            print(f"F16 conversion completed: {f16_file}")
        else:
            print("F16 conversion failed.")
    except Exception as e:
        print(f"F16 conversion error: {e}")
else:
    print("Skipping F16 conversion due to missing prerequisites.")


quantized_filename = f"{MODEL_NAME}-{QUANTIZATION_TYPE.lower()}.gguf"
q4_file = os.path.join(output_dir, quantized_filename)
quant_cmd = [quantizer_bin, f16_file, q4_file, QUANTIZATION_TYPE, QUANTIZATION_GROUP_SIZE]

if os.path.exists(quantizer_bin) and os.path.exists(f16_file):
    print(f"Starting {QUANTIZATION_TYPE} quantization...")
    try:
        quant_proc = subprocess.Popen(quant_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                      text=True, encoding="utf-8", errors="replace")
        for line in quant_proc.stdout:
            print(line, end="")
        quant_proc.wait()
        if quant_proc.returncode == 0 and os.path.exists(q4_file):
            size_mb = os.path.getsize(q4_file) / 1e6
            print(f"Quantization completed. GGUF {QUANTIZATION_TYPE} file ({size_mb:.2f} MB): {q4_file}")
            print(f"Delete F16 version if you don't need it")
        else:
            print(f"{QUANTIZATION_TYPE} quantization failed.")
    except Exception as e:
        print(f"Quantization error: {e}")
else:
    print("Skipping quantization due to missing prerequisites.")
