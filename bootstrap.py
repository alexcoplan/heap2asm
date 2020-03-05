#!/usr/bin/env python3

import subprocess
import os
import stat
import platform

def run(cmd):
  cmd_s = " ".join(cmd)
  print(f"Running: {cmd_s}")
  subprocess.check_call(cmd)

def plat_str():
  return platform.system().lower()

build_dir = 'build'
heap_suffix = f'amd64-{plat_str()}' # assume x64
heap_name = f"heap2asm.{heap_suffix}"
script_name = "h2a.sh"

def artefact(path):
  return os.path.join(build_dir, path)

def make_executable(file):
  st = os.stat(file)
  os.chmod(file, st.st_mode | stat.S_IEXEC)

def main():
  if not os.path.exists(build_dir):
    os.makedirs(build_dir)

  heap_path = artefact(heap_name)
  run(['ml-build', 'heap2asm.cm', 'Main.main', heap_path])

  script_path = artefact(script_name)
  with open(script_path, 'w') as f:
    f.write("#!/bin/bash\n")
    f.write(f'sml @SMLload={heap_path} "$@"\n')

  make_executable(script_path)

  out_path = artefact('heap2asm')
  run(['./heap2exec', script_path, heap_path, out_path])
  print(f"All done. Final executable in {out_path}")

if __name__ == '__main__':
  main()
