import subprocess
import psutil


def run_command(cmd_call):
    proc = subprocess.Popen(
        cmd_call,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE)
    so, se = proc.communicate()
    return so.decode("utf-8"), se.decode("utf-8")


def get_memory_bandwidth():
    raise NotImplementedError()


def get_cache_size(unit=''):
    # Read out all cache sizes (L1d, L1i, L2, L3, L4)
    cmd_list_sizes = "getconf -a | grep CACHE_SIZE | sed -r 's/\S+\s+//'"
    response, std_err = run_command(cmd_list_sizes)
    # And sum them up
    cache_size = float(sum([int(x) for x in response.split("\n") if len(x)]))
    # Optional: get in KiB or MiB
    if unit.lower() in ('kb', 'kib', 'mb', 'mib'):
        cache_size = cache_size / 1028
    if unit.lower() in ('mb', 'mib'):
        cache_size = cache_size / 1028
    return round(cache_size, 2)


def get_cpu_core_temperatures():
    return [x.current for x in psutil.sensors_temperatures()['coretemp']]
