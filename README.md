<div align="center">

# pyloudnorm-eval
Evaluation of a number of loudness meter implementations.

[Code (pyloudnorm)](https://github.com/csteinmetz1/pyloudnorm) | [Paper](https://csteinmetz1.github.io/pyloudnorm-eval/paper/pyloudnorm_preprint.pdf) | [Video]()

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
The original repo is located here: [https://github.com/BrechtDeMan/loudness.py.git](https://github.com/BrechtDeMan/loudness.py.git).
However, there are a few issues that make it difficult to run via our testbench. 
Therefore, we will install via our branch, which has a few changes, but doesn't change the algorithm implementation. 
```
git clone https://github.com/csteinmetz1/loudness.py.git
mv loudness.py loudness_py
```
Note you need to rename the resulting directory so it can be imported.


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

In order to use essentia make sure you create an environment in the following manner. Make sure to go back to the top level directory first.

```
cd ../.. # go back up
python3 -m venv env/ --system-site-packages
source env/bin/activate 
pip install -r requirements.txt
```

## Data


## Run 

Now run the evaluation, which will measure the loudness of all files in the `data/` directory and store the results in a text file.
This should take around 60 seconds.

```
python eval.py > results.txt
```

Optionally, you can run the fine-detail frequency test,
```
python eval.py -f
```
of the speed test to produce timings on your platform.
```
python eval.py -s 
```