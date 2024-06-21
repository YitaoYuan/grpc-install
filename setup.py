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

def rm_if_exist(d):
    if os.path.exists(d):
        echo_run(f"rm -r {d}")

def repo_name(url):
    return url.split('/')[-1]

git_url = "https://github.com/grpc/grpc"
software = repo_name(git_url)
root = f"/data/software/{software}"
module_path = f"/usr/share/modules/modulefiles/{software}"
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
if not os.path.exists(module_path):
    echo_run(f"mkdir -p {module_path}")

def install_pkg(ver):
    cd(src)
    old_src_path = os.path.join(src, software)
    src_name = f"{software}-{ver}"
    src_path = os.path.join(src, src_name)
    rm_if_exist(src_path)
    rm_if_exist(old_src_path)
    echo_run(f"git clone -b {ver} --depth 1 {git_url}")
    echo_run(f"mv {old_src_path} {src_path}")
    cd(src_path)
    echo_run(f"git submodule update --init --depth 1 -j {os.cpu_count()}")

    build_path = os.path.join(build, src_name)
    install_path = os.path.join(install, src_name)
    rm_if_exist(build_path)

    # use CMAKE_INSTALL_PREFIX instead of --install-prefix to be compatible with old cmake
    echo_run(f"cmake -DCMAKE_INSTALL_PREFIX={install_path} -S {src_path} -B {build_path}") 
    cd(build_path)

    echo_run(f"make -j {os.cpu_count()} install")

    re2pc_src = os.path.join(src_path, "third_party", "re2", "re2.pc")
    re2pc_dst_dir = os.path.join(install_path, "lib", "pkgconfig")
    re2pc_dst = os.path.join(re2pc_dst_dir, "re2.pc")
    lines = []
    with open(re2pc_src, "r") as f:
        lines = f.readlines()
    lines = [f"prefix={install_path}\n", "includedir=${prefix}/include\n", "libdir=${prefix}/lib\n"] + lines[2:]
    with open(re2pc_dst, "w") as f:
        f.writelines(lines)
    print(f"Generating {re2pc_dst}")

    module_file = os.path.join(module_path, ver)
    print(f"Installing modulefile: {module_file}")
    with open(module_file, "w") as f:
        bin_path = os.path.join(install_path, "bin")
        include_path = os.path.join(install_path, "include")
        lib_path = os.path.join(install_path, "lib")
        pkgconfig_path = os.path.join(lib_path, "pkgconfig")
        cmake_path = os.path.join(lib_path, "cmake")
        f.write(f"#%Module1.0\nconflict {software}\nprepend-path PATH {bin_path}\nprepend-path CPATH {include_path}\nprepend-path LD_LIBRARY_PATH {lib_path}\nprepend-path PKG_CONFIG_PATH {pkgconfig_path}\nprepend-path CMAKE_PREFIX_PATH {install_path}\nprepend-path CMAKE_MODULE_PATH {cmake_path}")

install_pkg(version)