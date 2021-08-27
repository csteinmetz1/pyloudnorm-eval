import subprocess
import soundfile as sf

# import our loudness libraries
import pyloudnorm as pyln
import loudness_py.loudness
import essentia.standard

def measure_pyloudnorm(filepath, mode="default"):
    data, sr = sf.read(filepath)

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

def measure_loudness_py(filepath):
    data, sr = sf.read(filepath)
    loudness = loudness_py.loudness.calculate_loudness(data, int(sr))
    return loudness

def measure_essentia(filepath):
    loader = essentia.standard.AudioLoader(filename=filepath)
    audio, sr, nchs, md5, bit_rate, codec = loader()

    meter = essentia.standard.LoudnessEBUR128(sampleRate=sr, hopSize=0.1)
    loudness = meter(audio)[2]

    return loudness