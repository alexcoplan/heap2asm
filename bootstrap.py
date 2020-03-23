#!/usr/bin/env python3

import subprocess
import os
import stat
import platform
import sys

from typing import List

logbuf = ""
quiet = True

def log(msg : str) -> None:
  global logbuf
  logbuf += msg
  if not quiet:
    sys.stdout.write(msg)

def logln(msg : str) -> None:
  log(msg + "\n")

def fail() -> None:
  if quiet: # if we have been keeping quiet, print log up to this point.
    print(logbuf)
  exit(1)

def run(cmd : List[str]) -> None:
  log("Running " + " ".join(cmd) + " ... ")
  res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  if res.returncode == 0:
    logln("OK")
    return
  logln("FAILED")
  stdout = res.stdout.decode("utf-8").strip()
  stderr = res.stderr.decode("utf-8").strip()
  if len(stdout) > 0:
    logln("Output (stdout):")
    log(stdout)
  if len(stderr) > 0:
    logln("Output (stderr):")
    log(stderr)

  fail()

def plat_str() -> str:
  return platform.system().lower()

build_dir = 'build'
script_name = "h2a.sh"

def artefact(path : str) -> str:
  return os.path.join(build_dir, path)

def make_executable(file : str) -> None:
  st = os.stat(file)
  os.chmod(file, st.st_mode | stat.S_IEXEC)

def main() -> None:
  if "SMLNJ_HOME" in os.environ:
    home = os.environ["SMLNJ_HOME"]
  else:
    home = "/usr/local/smlnj"

  if not os.path.exists(home):
    print("smlnj not found!")
    exit(1)

  if not os.path.exists(build_dir):
    os.makedirs(build_dir)

  arch_opsys = os.path.join(home, "bin/.arch-n-opsys")
  res = subprocess.run(arch_opsys, stdout=subprocess.PIPE, check=True)
  info_parts = res.stdout.decode("utf-8").split(";")
  info = {}
  for datum in info_parts:
    key, value = datum.split("=")
    info[key.strip()] = value.strip()

  if "HEAP_SUFFIX" not in info:
    print("Unknown HEAP_SUFFIX!")
    exit(1)

  heap_suffix = info["HEAP_SUFFIX"]
  arch = info["ARCH"]

  heap_name = f"heap2asm.{heap_suffix}"
  heap_path = artefact(heap_name)
  run(['ml-build', 'heap2asm.cm', 'Main.main', heap_path])

  script_path = artefact(script_name)
  with open(script_path, 'w') as f:
    f.write("#!/bin/bash\n")
    f.write(f'sml @SMLload={heap_path} "$@"\n')

  make_executable(script_path)

  cmd = ['./heap2exec']
  if arch == "x86":
    cmd.append('-32')

  cmd += [script_path, heap_path, artefact('heap2asm')]
  run(cmd)

if __name__ == '__main__':
  quiet = False # if running on command-line, be verbose
  main()
