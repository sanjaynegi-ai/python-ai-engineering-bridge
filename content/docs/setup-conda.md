# Using Conda Instead of uv

The course uses uv throughout, and that's what we recommend. If your team already standardises on Conda (Anaconda, Miniconda or Miniforge), you can follow the course with a Conda environment that provides Python, and pip for the packages. This page explains how.

Use one approach consistently. In particular, don't install the course's packages with `conda install`: the versions available on Conda channels differ from the ones the course tested. Use Conda for **Python**, and pip for **packages**.

## What you give up

The same as with `venv`: no lockfiles for your own projects, and no `uv run`. See [`setup-venv.md`](setup-venv.md#what-you-give-up).

## 1. The course repository

Create an environment with Python 3.13 and pip, then install the pinned packages from the repository root:

```bash
conda create -n skillup -c conda-forge python=3.13 pip
conda activate skillup
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`requirements.txt` is generated from `uv.lock`, so you get exactly the tested versions. When `git pull` brings a new `requirements.txt`, run the last command again.

Newer versions of the Anaconda distribution ask you to accept the terms of service for its default channels. `-c conda-forge` uses the community channel instead, which has no such step. If your company provides its own channel, use that.

## 2. Your projects

Use a separate environment for each project, so their dependencies don't interfere. For example, for Project 02:

```bash
conda create -n incident-api -c conda-forge python=3.13 pip
conda activate incident-api
cd ~/skillup/incident-api
python -m pip install --upgrade pip
python -m pip install -e . --group dev
```

`-e .` installs the project in editable mode, with its dependencies; `--group dev` adds pytest, Ruff and the other development tools. It needs pip 25.1 or newer.

Then translate the workbooks' `uv` commands as in [`setup-venv.md`](setup-venv.md#translating-workbook-commands), with your Conda environment activated.

## Notebooks

In VS Code, select the `skillup` Conda environment as the notebook kernel. In JupyterLab, start it from the activated environment: `jupyter lab`.

## Further reading

- [Managing environments with Conda](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html)
