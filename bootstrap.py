#!/usr/bin/env python3

import subprocess
import os
import stat
import platform
import sys

logbuf = ""
quiet = True

def log(msg):
  global logbuf
  logbuf += msg
  if not quiet:
    sys.stdout.write(msg)

def logln(msg):
  log(msg + "\n")

def fail():
  if quiet: # if we have been keeping quiet, print log up to this point.
    print(logbuf)
  exit(1)

def run(cmd, quiet, **kwargs):
  log("Running " + " ".join(cmd) + " ... ")
  res = subprocess.run(cmd, capture_output=True, **kwargs)
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
  run(['ml-build', 'heap2asm.cm', 'Main.main', heap_path], quiet)

  script_path = artefact(script_name)
  with open(script_path, 'w') as f:
    f.write("#!/bin/bash\n")
    f.write(f'sml @SMLload={heap_path} "$@"\n')

  make_executable(script_path)

  out_path = artefact('heap2asm')
  run(['./heap2exec', script_path, heap_path, out_path], quiet)

if __name__ == '__main__':
  quiet = False # if running on command-line, be verbose
  main()
