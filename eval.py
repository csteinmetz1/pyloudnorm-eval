import os
import sys
import glob
import time
import argparse
import numpy as np
import matplotlib.pyplot as plt

from measure import *

def run_timings(test_file, duration_sec, n_iters=1):

    pyloudnorm_default_time = 0
    pyloudnorm_deman_time = 0 
    loudness_py_default_time = 0
    ffmpeg_default_time = 0
    loudness_scanner_ffmpeg_time = 0
    essentia_default_time = 0

    for n in np.arange(n_iters):

        #sys.stdout.write(f" {n+1}/{n_iters}\r")
        #sys.stdout.flush()
        tic = time.perf_counter()
        pyloudnorm_default = measure_pyloudnorm(test_file)
        toc = time.perf_counter()
        pyloudnorm_default_time += toc-tic

        tic = time.perf_counter()
        pyloudnorm_deman = measure_pyloudnorm(test_file, mode="deman")
        toc = time.perf_counter()
        pyloudnorm_deman_time += toc-tic

        tic = time.perf_counter()
        loudness_py_default = measure_loudness_py(test_file)
        toc = time.perf_counter()
        loudness_py_default_time += toc-tic

        tic = time.perf_counter()
        ffmpeg_default = measure_ffmpeg(test_file)
        toc = time.perf_counter()
        ffmpeg_default_time += toc-tic

        tic = time.perf_counter()
        loudness_scanner_ffmpeg = measure_loudness_scanner(test_file, plugin="ffmpeg")
        toc = time.perf_counter()
        loudness_scanner_ffmpeg_time += toc-tic

        tic = time.perf_counter()
        essentia_default = measure_essentia(test_file)
        toc = time.perf_counter()
        essentia_default_time += toc-tic

    pyloudnorm_default_time /= n_iters
    pyloudnorm_deman_time /= n_iters 
    loudness_py_default_time /= n_iters
    ffmpeg_default_time /= n_iters
    loudness_scanner_ffmpeg_time /= n_iters
    essentia_default_time /= n_iters

    result = {
        "file" : test_file,
        "pyloudnorm (default)" : 
            {"dB LUFS" : pyloudnorm_default,
                "time" : pyloudnorm_default_time,
                "RTF" : duration_sec / pyloudnorm_default_time},
        "pyloudnorm (De Man)" : 
            {"dB LUFS" : pyloudnorm_deman,
                "time" : pyloudnorm_deman_time,
                "RTF" : duration_sec / pyloudnorm_deman_time},
        "loudness.py" :
            {"dB LUFS" : loudness_py_default,
                "time" : loudness_py_default_time,
                "RTF" : duration_sec / loudness_py_default_time},
        "ffmpeg" : 
            {"dB LUFS" : ffmpeg_default,
                "time" : ffmpeg_default_time,
                "RTF" : duration_sec / ffmpeg_default_time},
        "loudness-scanner" : 
            {"dB LUFS" : loudness_scanner_ffmpeg,
                "time" : loudness_scanner_ffmpeg_time,
                "RTF" : duration_sec / loudness_scanner_ffmpeg_time},
        "essentia" :
            {"dB LUFS" : essentia_default,
                "time" : essentia_default_time,
                "RTF" : duration_sec / essentia_default_time},
    }

    return result

def print_result(result):
    print(result["file"])
    print("-" * 48)
    for key, val in result.items():
        if key != "file":
            print(f"{key:22s}  {val['dB LUFS']: 2.2f} dB LUFS   {val['time']*1e3: 4.1f} ms    {val['RTF']:0.2f}x ")
    print()

def run_speed_test(n_iters=100, sample_rate=48e3):

    # we test at time durations of 
    # 1 sec, 10 sec, 30 sec, 1 min, 5 min

    if not os.path.isdir("data/noise"):
        os.makedirs("data/noise")

    durations = [1, 10, 30, 60, 5*60]
    results = []

    for duration_sec in durations:
        print(f"Timing {duration_sec} sec")
        samples = int(duration_sec * sample_rate)
        signal = (np.random.rand(samples, 2) * 2) - 1

        test_file = os.path.join("data", "noise", f"{duration_sec:0.1f}_sec.wav")
        sf.write(test_file, signal, int(sample_rate))

        result = run_timings(test_file, duration_sec, n_iters)
        results.append(result)

    RTFs = {
        "pyloudnorm (default)" : [],
        "pyloudnorm (De Man)" : [],
        "loudness.py" : [],
        "ffmpeg" : [],
        "loudness-scanner" : [],
        "essentia" : [],
    }

    for file_result in results:
        print_result(file_result)

        for key, val in file_result.items():
            if key != "file":
                RTFs[key].append(val["RTF"])

    for impl, RTFs in RTFs.items():
        print(f"{impl:22s} RTF: mean {np.mean(RTFs):2.2f}x  std {np.std(RTFs):2.2f}")

def run_freq_test(gain=-6, 
                  start=1, 
                  stop=24000, 
                  num_points=100, 
                  fs=48000, 
                  t=10.0, 
                  figdir="figures/"):

    freqs = np.linspace(start, stop, num=num_points)
    freqs = np.logspace(0, 4, num=num_points) * 2.40

    if not os.path.isdir("data/freqs"):
        os.makedirs("data/freqs")

    results = {
        "pyloudnorm (Default)" : [],
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
        signal = np.pad(signal, (22050, 22050))
        test_file = os.path.join("data", "freqs", f"{f:0.1f}Hz--{gain:0.1f}dB.wav")
        sf.write(test_file, signal, fs)
        data, sr = sf.read(test_file)

        pyloudnorm_default = measure_pyloudnorm(test_file)
        pyloudnorm_deman = measure_pyloudnorm(test_file, mode="deman")
        loudness_py_default = measure_loudness_py(test_file)
        ffmpeg_default = measure_ffmpeg(test_file)
        loudness_scanner_ffmpeg = measure_loudness_scanner(test_file, plugin="ffmpeg")
        essentia_default = measure_essentia(test_file)
    
        results["pyloudnorm (Default)"].append(pyloudnorm_default)
        results["pyloudnorm (De Man)"].append(pyloudnorm_deman)
        results["loudness.py"].append(loudness_py_default)
        results["ffmpeg"].append(ffmpeg_default)
        results["loudness-scanner"].append(loudness_scanner_ffmpeg)
        results["essentia"].append(essentia_default)

    fig, ax = plt.subplots(figsize=(5,3))
    mean = None

    for key, val in results.items():
        plt.plot(freqs, val, label=key)

        if mean is None:
            mean = np.array(val)
        else:
            mean += np.array(val)

    plt.grid()
    plt.legend()
    plt.ylabel('Loudness (dB LUFS)')
    plt.xlabel('Frequency (Hz)')
    plt.tight_layout()
    plt.savefig(os.path.join(figdir, "1Hz-24kHz.pdf"))

    plt.xlim([4,30])
    plt.ylim([-45,-20])
    plt.ylabel('Loudness (dB LUFS)')
    plt.xlabel('Frequency (Hz)')
    plt.tight_layout()
    plt.savefig(os.path.join(figdir, "4Hz-30Hz.pdf"))

    ax = plt.gca()
    ax.relim()   
    ax.autoscale()
    plt.xlim([1000,1500])
    plt.ylim([-9,-7.5])
    plt.ylabel('Loudness (dB LUFS)')
    plt.xlabel('Frequency (Hz)')
    plt.tight_layout()
    plt.savefig(os.path.join(figdir, "1kHz-1.5kHz.pdf"))

    ax = plt.gca()
    ax.relim()   
    ax.autoscale()
    plt.ylabel('Loudness (dB LUFS)')
    plt.xlabel('Frequency (Hz)')
    plt.xlim([20000,24000])
    plt.ylim([-10,-2])
    plt.tight_layout()
    plt.savefig(os.path.join(figdir, "20kHz-24kHz.pdf"))

    plt.close('all')

    fig, ax = plt.subplots()

    mean = np.array(mean)/len(results.keys())

    for key, val in results.items():
        val = np.array(val)
        plt.plot(freqs, np.array(val) - mean, label=key)

    plt.grid()
    plt.legend()
    plt.xlim([4,10])
    plt.ylabel('Loudness (dB LUFS)')
    plt.xlabel('Frequency (Hz)')
    plt.tight_layout()
    plt.savefig(os.path.join(figdir, "1Hz-10Hz-mean-deviation.pdf"))

    ax = plt.gca()
    ax.relim()   
    ax.autoscale()
    plt.xlim([20,10000])
    plt.ylim([-0.2,0.2])
    plt.ylabel('Loudness (dB LUFS)')
    plt.xlabel('Frequency (Hz)')
    plt.tight_layout()
    plt.savefig(os.path.join(figdir, "20Hz-10kHz-mean-deviation.pdf"))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Path to file or directory of files to measure", type=str, default='data/')
    parser.add_argument("-f", "--freq", help="Frequnecy response test.", action="store_true")
    parser.add_argument("-n", "--num", help="Number of iterations to run over files for timings.", type=int, default=1)
    parser.add_argument("-p", "--points", help="Number of points (sinusoids) to evaluate models.", type=int, default=150)
    parser.add_argument("-s", "--speed", help="Perform speed benchmark.", action="store_true")

    args = parser.parse_args()

    if args.freq:
        run_freq_test(num_points=args.points)

    if args.speed:
        run_speed_test()

    if os.path.isfile(args.input):
        test_files = [args.input]
    elif os.path.isdir(args.input):
        test_files = glob.glob(os.path.join("data", "*.wav"))
        test_files = sorted(test_files)
    else:
        raise RuntimeError(f"Invalid input: '{args.input}'")

    # duplicate test files for multiple runs if set
    test_files = test_files * args.num

    print(f"Found {len(test_files)} files.")

    results = []

    for idx, test_file in enumerate(test_files):
        sys.stdout.write(f"* Measuring {idx+1}/{len(test_files)}\r")
        sys.stdout.flush()

        data, sr = sf.read(test_file)
        duration_sec = (data.shape[0]/sr)

        result = run_timings(test_file, duration_sec)

        results.append(result)
        print_result(result)
    
    RTFs = {
        "pyloudnorm (default)" : [],
        "pyloudnorm (De Man)" : [],
        "loudness.py" : [],
        "ffmpeg" : [],
        "loudness-scanner" : [],
        "essentia" : [],
    }

    for file_result in results:
        print_result(file_result)

        for key, val in file_result.items():
            if key != "file":
                RTFs[key].append(val["RTF"])

    for impl, RTFs in RTFs.items():
        print(f"{impl:22s} RTF: mean {np.mean(RTFs):2.2f}x  std {np.std(RTFs):2.2f}")

