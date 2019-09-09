## Installation / Environment Setup

### Install Homebrew and Python 3
```sh
/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
export PATH="/usr/local/bin:/usr/local/sbin:$PATH"
brew update
brew install python3  # Python 3
sudo pip3 install -U virtualenv  # system-wide install
```

### Create a new virtual environment for this project
We recommend that you run this from the root directory of this repo.
It will create a venv directory in your working directory.
```sh
virtualenv --system-site-packages -p python3 ./venv
```

### Activate the virtual environment
```sh
source ./venv/bin/activate  # sh, bash, ksh, or zsh
```

### Upgrade pip
```sh
pip install --upgrade pip
```

### Install requirements
Make sure you are in the root directory of this repo.
```sh
pip install -r requirements.txt
```
Now you should be ready to go!

### Deactivate environment when you are done
```sh
deactivate
```


## Installing FluidSynth and Sound Fonts

* Install FluidSynth : `brew install fluid-synth --with-libsndfile`
* Install this soundfont : http://www.schristiancollins.com/generaluser.php

`ln n -f GeneralUser\ GS\ 1.471/GeneralUser\ GS\ v1.471.sf2 ~/.fluidsynth/default_sound_font.sf2`
`fluidsynth -ni ~/.fluidsynth/default_sound_font.sf2 test.mid`
`fluidsynth -ni ~/.fluidsynth/default_sound_font.sf2  Melydi/melydi/midi_utils/test7.mid -F Melydi/melydi/midi_utils/test_synth.wav -r 44100`
