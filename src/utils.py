import sys

def log(*objs):
    if silent:
        return
    print("\033[0m", end="", flush=True)
    print(*objs, file=sys.stderr)
    print("\033[0m", end="", flush=True)

def warn(*objs):
    if silent:
        return
    print("\033[31m", end="", flush=True)
    print(*objs, file=sys.stderr)
    print("\033[0m", end="", flush=True)


