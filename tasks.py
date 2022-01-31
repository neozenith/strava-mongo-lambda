#!/usr/bin/env python3
# Standard Library
import os
import shlex
import shutil
import sys
from pathlib import Path
from subprocess import run

# NOTE:
# 1. python ./tasks.py
#    - Bootstrap venv and install invoke and create dummy decorator in interim
# 2. invoke <name of task>
#    - This should successfully import invoke and task decorator
try:
    # Third Party
    from invoke import task
except ImportError:
    task = lambda *args, **kwargs: lambda x: x  # noqa: E731

DEFAULT_PYPROJECT_CONFIG = """
[tool.black]
line-length = 120

[tool.isort]
profile = "black"
multi_line_output = 3
import_heading_stdlib = "Standard Library"
import_heading_firstparty = "Our Libraries"
import_heading_thirdparty = "Third Party"

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-v --color=yes"

"""

DEFAULT_FLAKE8_CONFIG = """
[flake8]
max-line-length=120
max-complexity = 10
exclude =
    # No need to traverse our git directory
    .git,
    # There's no value in checking cache directories
    __pycache__,
    # Ignore virtual environment folders
    .venv
"""

DEFAULT_REQUIREMENTS_DEV = """
invoke
flake8
isort
black
pytest
"""


@task
def format(c):
    """Autoformat code and sort imports."""
    c.run("black .")
    c.run("isort .")


@task
def lint(c):
    """Run linting and formatting checks."""
    c.run("black --check .")
    c.run("isort --check .")
    c.run("flake8 .")


@task(pre=[lint])
def test(c):
    """Run pytest."""
    c.run("python3 -m pytest")


@task
def build(c):
    """Build the lambda into the dist folder."""
    print("BUILDING...")
    _build_lambda("src", "dist", "requirements.txt")


@task(pre=[build])
def deploy(c):
    """Package lambda and dependencies into a zip, upload to S3 and update target function code."""
    # Third Party
    import boto3

    session = boto3.session.Session(profile_name="play")
    s3_client = session.client("s3")
    lambda_client = session.client("lambda")

    PROJECT_NAME = "strava-mongo-lambda"
    BUCKET_NAME = "play-projects-joshpeak"
    FUNCTION_NAME = "strava-mongo-fetch"

    print("PACKAGING...")
    shutil.make_archive("code", "zip", "dist")

    print("UPLOADING...")
    s3_client.upload_file("code.zip", BUCKET_NAME, f"{PROJECT_NAME}/code.zip")

    print(f"DEPLOYING s3://{BUCKET_NAME}/{PROJECT_NAME}/code.zip --> {FUNCTION_NAME}")
    lambda_client.update_function_code(
        FunctionName=FUNCTION_NAME, S3Bucket=BUCKET_NAME, S3Key=f"{PROJECT_NAME}/code.zip"
    )


def _check_deps(filename):
    if os.path.isfile(filename):
        print(f"Installing deps from {filename}")
        _shcmd(f".venv/bin/python3 -m pip install -qq --upgrade -r {filename}")


def _check_config(filename, content):
    if not os.path.isfile(filename):
        print(f"Generating {filename} ...")
        with open(filename, "w+") as f:
            f.write(content)


def _shcmd(command, args=[], **kwargs):
    if "shell" in kwargs and kwargs["shell"]:
        return run(command, **kwargs)
    else:
        cmd_parts = command if type(command) == list else shlex.split(command)
        cmd_parts = cmd_parts + args
        return run(cmd_parts + args, **kwargs)


def _build_lambda(src_dir, out_dir, reqs):
    target = src_dir
    print(f"\nBUILD: {src_dir}")

    if not Path(src_dir).is_dir():
        raise Error(f"Could not build '{target}' because missing folder '{src_dir}'")

    print(f"CLEAN: {out_dir}")
    if Path(out_dir).is_dir():
        shutil.rmtree(out_dir)

    print(f"COPY: {src_dir} -> {out_dir}")
    shutil.copytree(src_dir, out_dir)

    # install deps
    print(f"DEPS: {reqs} -> {out_dir}")
    install_cmd = f".venv/bin/python3 -m pip install --target {out_dir} -r {reqs} --ignore-installed -qq"
    print(install_cmd)
    _shcmd(install_cmd)


if __name__ == "__main__":

    if len(sys.argv) >= 2 and sys.argv[1] in ["init"]:
        _shcmd("rm -rf .venv")
        _shcmd("python3 -m venv .venv")
        _shcmd(".venv/bin/python3 -m pip install --upgrade pip")

        _check_config("requirements-dev.txt", DEFAULT_REQUIREMENTS_DEV)
        _check_config("pyproject.toml", DEFAULT_PYPROJECT_CONFIG)
        _check_config(".flake8", DEFAULT_FLAKE8_CONFIG)

        _check_deps("requirements.txt")
        _check_deps("requirements-dev.txt")

    else:
        print("This script should be run as:\n\n./tasks.py init\n\n")
        print("This will self bootstrap a virtual environment but then use:\n\n")
        print(". ./.venv/bin/activate")
        print("invoke --list")
