
import sys
import traceback

print("Testing Torch/Audio...")
try:
    import torch
    print(f"Torch version: {torch.__version__}")
    import torchaudio
    print(f"Torchaudio version: {torchaudio.__version__}")
except:
    traceback.print_exc()

print("Done.")
