
import sys
import traceback

print("Testing Demucs Import...")
try:
    import soundfile
    print(f"Soundfile version: {soundfile.__version__}")
    import demucs
    print("Demucs imported.")
    import demucs.separate
    print("Demucs.separate imported.")
except:
    traceback.print_exc()

print("Done.")
