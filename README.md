<div align="center">

# pyloudnorm-eval
Evaluation of a number of loudness meter implementations.

[Code (pyloudnorm)](https://github.com/csteinmetz1/pyloudnorm) | [Paper](paper/pyloudnorm_preprint.pdf) | [Video]()

</div>

## Setup

### Install essentia (macOS)

You will need homebrew.
```
brew tap MTG/essentia
brew install essentia --HEAD
```

For other platforms, please refer to the [essentia docs](https://essentia.upf.edu/documentation/installing.html).

### Install loudness.py

```
git clone https://github.com/BrechtDeMan/loudness.py.git
```

### Install loudness-scanner

```
git clone git://github.com/jiixyj/loudness-scanner.git
cd loudness-scanner
git submodule init
git submodule update
mkdir build
cd build
cmake ..
make
```

In order to use essentia make sure you create an environment in the following manner.

```
python3 -m venv env/ --system-site-packages
source env/bin/activate 
pip install -r requirements.txt
```

## Run 

Now run the evaluation, which will measure the loudness of all files in the `data/` directory.

```
python eval.py
```

Optionally, you can run the fine-detail frequency test,
```
python eval.py -f
```
of the speed test to produce timings on your platform.
```
python eval.py -s 
```