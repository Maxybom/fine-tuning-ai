import os
import sys
import subprocess
import importlib

BASE_MODEL_PATH = "codellama/CodeLlama-7b-Instruct-hf"               
LORA_ADAPTER_PATH = "./lora"                                         
MERGED_OUTPUT_PATH = "./merged-model"                                

required_packages = {
    "torch": "torch==2.3.0",
    "transformers": "transformers==4.44.2",
    "peft": "peft>=0.13.0",
    "accelerate": "accelerate",
    "safetensors": "safetensors",
    "sentencepiece": "sentencepiece"
}

for module_name, package in required_packages.items():
    if importlib.util.find_spec(module_name) is None:
        print(f"Installing missing dependency: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

print("Loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(BASE_MODEL_PATH, torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)

print("Applying LoRA adapter...")
try:
    model = PeftModel.from_pretrained(base_model, LORA_ADAPTER_PATH)
except TypeError as e:
    print(f"LoRA loading error: {e}")
    print("Attempting to upgrade PEFT...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "peft"])
    from peft import PeftModel
    model = PeftModel.from_pretrained(base_model, LORA_ADAPTER_PATH)

print("Merging weights...")
merged_model = model.merge_and_unload()

print("Saving merged model...")
os.makedirs(MERGED_OUTPUT_PATH, exist_ok=True)
merged_model.save_pretrained(MERGED_OUTPUT_PATH)
tokenizer.save_pretrained(MERGED_OUTPUT_PATH)

print("Merge completed successfully.")
print(f"Merged model saved to: {os.path.abspath(MERGED_OUTPUT_PATH)}")
print("You can now convert it to GGUF using the conversion script.")
