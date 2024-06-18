#!/usr/bin/python3
# encoding: utf-8

import os, sys

def echo_run(cmd):
    print(cmd)
    ret = os.system(cmd)
    if ret != 0:
       exit(ret)

def most_recent(d):
    file_name = os.listdir(d)
    file_list = [os.path.join(d, f) for f in file_name]
    time_list = [os.path.getmtime(file_name) for file_name in file_list]
    max_time = max(time_list)
    max_id = time_list.index(max_time)
    return file_name[max_id]

def cd(d):
    print(f"Into {d}")
    os.chdir(d)

root = "/data/software/grpc"
version = sys.argv[1]

log_file = os.path.join(root, "log.txt")
if os.path.exists(log_file):
    echo_run(f"rm {log_file}")

dirs = ["src", "build", "install"]
for d in dirs:
    exec(f"{d} = os.path.join(root, '{d}')")
    absdir = eval(f"{d}")
    echo_run(f"mkdir -p {absdir}")

# pkg_list = os.listdir(pkg)
# pkg_tail = ".tar.xz"
module_path = "/usr/share/modules/modulefiles/grpc"
if not os.path.exists(module_path):
    echo_run(f"mkdir -p {module_path}")

def install(ver):
    cd(src)
    echo_run(f"git clone -b {ver} --depth 1 https://github.com/grpc/grpc")
    old_src_path = os.path.join(src, "grpc")
    src_name = f"grpc-{ver}"
    src_path = os.path.join(src, src_name)
    echo_run(f"mv {old_src_path} {src_path}")
    cd(src_path)
    echo_run(f"git submodule update --init --depth 1")

    build_path = os.path.join(build, src_name)
    install_path = os.path.join(install, src_name)
    if os.path.exists(build_path):
        echo_run(f"rm -r {build_path}")

    echo_run(f"cmake -S {src_path} -B {build_path} --install-prefix {install_path}")
    cd(build_path)

    echo_run(f"make -j {os.cpu_count()} install")

    module_file = os.path.join(module_path, pkg_file[:-len(pkg_tail)])
    with open(module_file, "w") as f:
        bin_path = os.path.join(install_path, "bin")
        include_path = os.path.join(install_path, "include")
        lib_path = os.path.join(install_path, "lib")
        pkgconfig_path = os.path.join(lib_path, "pkgconfig")
        cmake_path = os.path.join(lib_path, "cmake")
        print(pkgconfig_path)
        f.write(f"#%Module1.0\nconflict dpdk\nprepend-path PATH {bin_path}\nprepend-path CPATH {include_path}\nprepend-path LD_LIBRARY_PATH {lib_path}\nprepend-path PKG_CONFIG_PATH {pkgconfig_path}\nprepend-path CMAKE_PREFIX_PATH {install_path}\nprepend-path CMAKE_MODULE_PATH {cmake_path}")

install(version)