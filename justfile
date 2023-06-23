# show this list
default:
    just --list

# format python and nix
format:
    isort . --skip-gitignore
    black .
    alejandra .
