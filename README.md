# Kestrel

This is Kestrel Project.

## Setup

### pyenv 설치

```
brew update
brew install pyenv
```

```
.bash_profile
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
```

### python 설치

```
pyenv install 3.11
pyenv global 3.11
python --version
```

### poetry 설치

```
pip3 install poetry
```

```
poetry shell
```

```
poetry update
```

### Sevice Start

```
poe start
```