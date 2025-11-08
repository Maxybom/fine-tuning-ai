# fine-tuning-ai
- [Description](#description)
- [Requirements](#requirements)
- [Google Colab](#google-colab)
- [Merge LoRa](#merge-lora)
- [Convert and quantization](#convert-and-quantization)
- [Credits](#credits)

# Description

  After obtaining one or more LoRA files—either manually or using the scripts available on Google Colab (see index)—you can use the scripts included in this repository to:
  
  Merge multiple LoRA files into a single checkpoint
  Convert them to GGUF format
  Quantize them to optimize efficiency and reduce memory usage
  Conversion and Quantization with llama.cpp
  The conversion to GGUF format and quantization are based on llama.cpp, already configured as a submodule. The compilation script runs automatically when you start the gguf_convert_quantization.py script.

Inside the tools folder, there is a script dedicated to converting datasets into Prompt::completion format. This script allows you to transform a raw .txt file (with lines in prompt::completion format) into a .json file compatible with fine-tuning an LLM model. It is designed to be used in combination with the Colab scripts provided.

# Requirements

To compile llama.cpp and use the quantization tools, the following dependencies are required:

General:
 - CMake version 3.16 or higher
 - Python 3.8 or higher 
 - Git for submodule management

Windows:
 - One of the following CMake generators:
 - Visual Studio 17 2022 (recommended)
 - Visual Studio 16 2019
 - MinGW Makefiles
 - Ninja
 - Visual Studio must include the "Desktop development with C++" workload

macOS:
 - Xcode
 - CMake
 - Ninja or Unix Makefiles
 - Clang++ compiler

Linux:
 - build-essential (includes make, g++, etc.)

# Google Colab

Follow the scripts provided for common GPU setups on Google Colab.

- TPU v6 training script:
  https://colab.research.google.com/drive/1TlmYhz7bExne8j7xhbgJ3Z6uMn9VvTDJ?usp=sharing

- A100 training script:
  https://colab.research.google.com/drive/12JQMprCQCCBYUTUC3HMLNsQ2ipNNncEZ?usp=sharing

- T4/L4 training script:
  https://colab.research.google.com/drive/1sxTxXmeWbkZBYI5N6C4QO4d-HwPJsSiB?usp=sharing

 # Merge-LoRa

 The merge.py script is used to merge a LoRA adapter into a base LLM checkpoint. To execute it, simply run the Python script — but before doing so, you can check input parameters:
 
 These variables are defined at the top of the script, directly below the import statements, under the # configuration comment (lines 7–9):
 - base_model_path: the path to the original LLM checkpoint
 - lora_adapter_path: the path to the LoRA file to be merged
 - merged_output_path: the destination directory for the merged model

# Convert and quantization

The script gguf_convert_quantization.py is used to convert a fine-tuned LLM — for example, one produced via merge.py — into the GGUF format and quantize it according to the target hardware.

In addition to the quantized model, the script also generates an f16 version. If this full-precision version is not needed, it can be safely deleted.

This script relies on llama.cpp for both conversion and quantization. If llama.cpp has not yet been compiled, the script will automatically invoke compile_llama_cpp.py to build the required binaries.

If an error occurs during execution, check the terminal output carefully — it likely indicates that one or more required tools (e.g., CMake, compiler, generator) are missing or misconfigured.

Configuration Parameters:
- The following variables are defined at the top of the script, under the # Configuration section:
- MODEL_NAME = "model"                     # Base name for output files
- QUANTIZATION_TYPE = "Q4_K_M"            # Quantization mode (e.g., Q4_K_M, Q5_1, Q6_K)
- QUANTIZATION_GROUP_SIZE = "8"           # Group size for quantization (typically 8 or 32)
- MODEL_INPUT_DIR = "./merged-model"      # Path to the Hugging Face model directory or local path
- OUTPUT_DIR = "./gguf-output"            # Destination folder for converted and quantized files

# Credits
Credits to llama.cpp (see submodule in the extern folder) for providing the core logic used in quantization and GGUF conversion. The script gguf_convert_quantization.py automatically calls their build and conversion routines.
