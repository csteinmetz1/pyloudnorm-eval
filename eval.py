import os
import sys
import glob
import argparse
import subprocess
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt

# import our loudness libraries
import pyloudnorm as pyln
import loudness_py.loudness 
import essentia.standard

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

def measure_essentia(filepath):
    loader = essentia.standard.AudioLoader(filename=filepath)
    audio, sr, nchs, md5, bit_rate, codec = loader()

    meter = essentia.standard.LoudnessEBUR128(sampleRate=sr, hopSize=0.1)
    loudness = meter(audio)[2]

    return loudness

def run_freq_test(gain=-6, start=1, stop=24000, num_points=100, fs=48000, t=1.0):

    freqs = np.linspace(start, stop, num=num_points)

    if not os.path.isdir("data/freqs"):
        os.makedirs("data/freqs")

    results = {
        "pyloudnorm (default)" : [],
        "pyloudnorm (De Man)" : [],
        "loudness.py" : [],
        "ffmpeg" : [],
        "loudness-scanner" : [],
        "essentia" : [],
    }

    for idx, f in enumerate(freqs):
        sys.stdout.write(f"* Evaluating {f:0.1f} Hz - {idx+1}/{len(freqs)}\r")
        sys.stdout.flush()
        samples = np.linspace(0, t, int(fs*t), endpoint=False)
        signal = 10**(gain/20) * np.cos(2 * np.pi * f * samples)
        test_file = os.path.join("data", "freqs", f"{f:0.1f}Hz--{gain:0.1f}dB.wav")
        sf.write(test_file, signal, fs)
        data, sr = sf.read(test_file)

        pyloudnorm_default = measure_pyloudnorm(data, sr)
        pyloudnorm_deman = measure_pyloudnorm(data, sr, mode="deman")
        loudness_py_default = measure_loudness_py(data, int(sr))
        ffmpeg_default = measure_ffmpeg(test_file)
        loudness_scanner_ffmpeg = measure_loudness_scanner(test_file, plugin="ffmpeg")
        essentia_default = measure_essentia(test_file)
    
        results["pyloudnorm (default)"].append(pyloudnorm_default)
        results["pyloudnorm (De Man)"].append(pyloudnorm_deman)
        results["loudness.py"].append(loudness_py_default)
        results["ffmpeg"].append(ffmpeg_default)
        results["loudness-scanner"].append(loudness_scanner_ffmpeg)
        results["essentia"].append(essentia_default)

    fig, ax = plt.subplots()

    for key, val in results.items():
        plt.plot(freqs, val, label=key)

    plt.grid()
    plt.legend()

    plt.xlim([1,10])
    plt.savefig("1Hz-10Hz.png")

    ax = plt.gca()
    ax.relim()   
    ax.autoscale()
    plt.xlim([1000,4000])
    plt.ylim([-8,-5.5])
    plt.savefig("1kHz-4kHz.png")

    ax = plt.gca()
    ax.relim()   
    ax.autoscale()
    plt.xlim([20000,24000])
    plt.ylim([-10,-2])
    plt.savefig("20kHz-24kHz.png")



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Path to file or directory of files to measure", type=str)
    parser.add_argument("-f", "--freq", help="Frequnecy response test.", action="store_true")
    args = parser.parse_args()

    if args.freq:
        run_freq_test()

    if os.path.isfile(args.input):
        test_files = [args.input]
    elif os.path.isdir(args.input):
        test_files = glob.glob(os.path.join("data", "*.wav"))
        test_files = sorted(test_files)
    else:
        raise RuntimeError(f"Invalid input: '{args.input}'")

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
        essentia_default = measure_essentia(test_file)

        results.append({
            "file" : test_file,
            "pyloudnorm (default)" : pyloudnorm_default,
            "pyloudnorm (De Man)" : pyloudnorm_deman,
            "loudness.py" : loudness_py_default,
            "ffmpeg" : ffmpeg_default,
            "loudness-scanner (ffmpeg)" : loudness_scanner_ffmpeg,
            "essentia" : essentia_default,
        })
    
    for file_result in results:
        print(file_result["file"])
        for key, val in file_result.items():
            if key != "file":
                print(f"{key}  {val:2.2f}")
        print()
