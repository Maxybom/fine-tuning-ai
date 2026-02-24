import os
import gc
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

BASE_MODEL_PATH = "HuggingFaceTB/SmolLM-135M-Instruct"               
LORA_ADAPTER_PATH = "./lora"                                         
MERGED_OUTPUT_PATH = "./merged-model"                                

print("Loading base model...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL_PATH, 
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True
)
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_PATH)

print("Applying LoRA adapter...")
model = PeftModel.from_pretrained(base_model, LORA_ADAPTER_PATH)

print("Merging weights...")
merged_model = model.merge_and_unload()

del model      
del base_model 
gc.collect()     

print("Saving merged model...")
os.makedirs(MERGED_OUTPUT_PATH, exist_ok=True)
merged_model.save_pretrained(MERGED_OUTPUT_PATH)
tokenizer.save_pretrained(MERGED_OUTPUT_PATH)

print(f"Merge completed: {os.path.abspath(MERGED_OUTPUT_PATH)}")