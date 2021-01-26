from os.path import join, exists
from shutil import rmtree
from subprocess import run
from copy import copy

from os import makedirs
import os

from invoke import task
from faasmtools.build import CMAKE_TOOLCHAIN_FILE, WASM_SYSROOT
from tasks.env import THIRD_PARTY_DIR

MXNET_DIR = join(THIRD_PARTY_DIR, "mxnet")

# See the MXNet CPP guide for more info:
# https://mxnet.apache.org/api/cpp.html

INSTALLED_LIBS = [
    "mxnet",
    "dmlc",
]

INSTALLED_HEADER_DIRS = [
    join(WASM_SYSROOT, "include", "mxnet"),
    join(WASM_SYSROOT, "include", "dmlc"),
]

INSTALLED_LIBS_DIR = join(WASM_SYSROOT, "lib", "wasm32-wasi")


@task
def uninstall(ctx):
    """
    Removes installed MXNet components
    """
    for lib_name in INSTALLED_LIBS:
        base_path = join(INSTALLED_LIBS_DIR, lib_name)
        lib_paths = [
            "{}.so".format(base_path),
            "{}.a".format(base_path),
        ]

        for lib_path in lib_paths:
            if exists(lib_path):
                print("Removing {}".format(lib_path))
                os.remove(lib_path)

    for header_dir in INSTALLED_HEADER_DIRS:
        if exists(header_dir):
            print("Removing {}".format(header_dir))
            rmtree(header_dir)


@task(default=True)
def install(ctx, clean=False, shared=True):
    """
    Installs the MXNet system library
    """
    work_dir = join(MXNET_DIR, "build")

    if clean:
        rmtree(work_dir)

    makedirs(work_dir, exist_ok=True)

    env_vars = copy(os.environ)

    # Set up different flags for shared/ static
    shared_flag = "ON" if shared else "OFF"

    # Note we have to build a shared lib for use with Python
    cmake_cmd = [
        "cmake",
        "-GNinja",
        "-DFAASM_BUILD_SHARED={}".format(shared_flag),
        "-DCMAKE_TOOLCHAIN_FILE={}".format(CMAKE_TOOLCHAIN_FILE),
        "-DCMAKE_BUILD_TYPE=Release",
        "-DCMAKE_INSTALL_PREFIX={}".format(WASM_SYSROOT),
        "-DCMAKE_INSTALL_LIBDIR=lib/wasm32-wasi",
        "-DCMAKE_DL_LIBS=",
        "-DUSE_CUDA=OFF",
        "-DUSE_LAPACK=OFF",
        "-DUSE_MKL_IF_AVAILABLE=OFF",
        "-DUSE_F16C=OFF",
        "-DUSE_SSE=OFF",
        "-DUSE_S3=OFF",
        "-DUSE_OPENMP=OFF",
        "-DUSE_OPENCV=OFF",
        "-DUSE_INTGEMM=OFF",
        "-DUSE_TENSORRT=OFF",
        "-DUSE_OPERATOR_TUNING=OFF",
        "-DBUILD_CPP_EXAMPLES=OFF",
        "-DUSE_SIGNAL_HANDLER=OFF",
        "-DUSE_CCACHE=OFF",
        "-DUSE_CPP_PACKAGE=ON",
        "-DMXNET_BUILD_SHARED_LIBS={}".format(shared_flag),
        "-DBUILD_SHARED_LIBS={}".format(shared_flag),
        MXNET_DIR,
    ]

    cmake_str = " ".join(cmake_cmd)
    print(cmake_str)

    print("\n--------------------\nMXNET CMAKE\n-------------------\n")
    run(cmake_str, shell=True, check=True, cwd=work_dir, env=env_vars)

    print("\n--------------------\nMXNET NINJA\n-------------------\n")
    run("ninja -v mxnet", shell=True, check=True, cwd=work_dir, env=env_vars)

    print("\n--------------------\nMXNET INSTALL\n-------------------\n")
    run("ninja install", shell=True, check=True, cwd=work_dir)
