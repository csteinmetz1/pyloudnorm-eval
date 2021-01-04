import os
import sys
import glob
import subprocess
import soundfile as sf
import numpy as np

# import our loudness libraries
import pyloudnorm as pyln
import loudness_py.loudness 

def measure_pyloudnorm(data, sr, mode="default"):
    if mode == "default":
        meter = pyln.Meter(sr)
    elif mode == "deman":
        meter = pyln.Meter(sr, filter_class="DeMan")

    loudness = meter.integrated_loudness(data)
    return loudness

def measure_ffmpeg(filepath):
    ffmpeg_command = ["ffmpeg", "-i", filepath, "-af", "loudnorm=print_format=summary", "-f", "null", "-"]

    pipe = subprocess.run(ffmpeg_command,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       bufsize=10**8)

    # parse loudness value
    val = str(pipe.stderr.decode("utf-8") ).split('\n')
    loudness = [v for v in val if "Input Integrated" in v][0]
    loudness = float(loudness.split(' ')[-2])
    return loudness

def measure_loudness_scanner(filepath, plugin='ffmpeg'):
    loudness_command = ["./loudness-scanner/build/loudness", "scan", f"--force-plugin={plugin}", filepath]

    pipe = subprocess.run(loudness_command,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE,
                       bufsize=10**8)

    # debug
    val = str(pipe.stdout.decode("utf-8"))
    val = val.split()[0]
    loudness = float(val)
    return loudness

def measure_loudness_py(data, sr):
    loudness = loudness_py.loudness.calculate_loudness(data, sr)
    return loudness

if __name__ == '__main__':

    test_files = glob.glob(os.path.join("data", "*.wav"))
    print(f"Found {len(test_files)} files.")

    results = []

    for idx, test_file in enumerate(test_files):
        sys.stdout.write(f"* Measuring {idx+1}/{len(test_files)}\r")
        sys.stdout.flush()
        data, sr = sf.read(test_file)

        pyloudnorm_default = measure_pyloudnorm(data, sr)
        pyloudnorm_deman = measure_pyloudnorm(data, sr, mode="deman")
        loudness_py_default = measure_loudness_py(data, int(sr))
        ffmpeg_default = measure_ffmpeg(test_file)
        loudness_scanner_ffmpeg = measure_loudness_scanner(test_file, plugin="ffmpeg")

        results.append({
            "file" : test_file,
            "pyloudnorm (default)" : pyloudnorm_default,
            "pyloudnorm (De Man)" : pyloudnorm_deman,
            "loudness.py" : loudness_py_default,
            "ffmpeg" : ffmpeg_default,
            "loudness-scanner (ffmpeg)" : loudness_scanner_ffmpeg,
        })
    
    for file_result in results:
        print(file_result["file"])
        for key, val in file_result.items():
            if key != "file":
                print(f"{key}  {val:2.2f}")
        print()
