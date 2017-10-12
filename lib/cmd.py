#!/usr/bin/env python3.5
import shlex
import subprocess

def cmd(cmd):
    if not cmd.startswith(r'sudo '):
        cmd = 'sudo ' + cmd
    
    args = shlex.split(cmd)
    
    output = subprocess.Popen(args, shell = False, stdout = subprocess.PIPE,
        stderr = subprocess.PIPE)
    stdout, stderr = output.communicate()
    stdout = stdout.decode('utf-8').strip()
    stderr = stderr.decode('utf-8').strip()
    exit_status = output.returncode
    
    return (stdout, stderr, exit_status)