# pyloudnorm-eval
Evaluation of a number of loudness meter implementations

## Setup

```
pip install -r requirements.txt
```

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

## Run 

Now run the evaluation, which will measure the loudness of all files in the `data/` directory.

```
python eval.py
```