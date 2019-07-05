from proc import run_command

affinity = 1
cmd_call = 'echo test'
cmd_call = f'Numactl -N {affinity} -m {affinity} {cmd_call}'
so, se = run_command(cmd_call)

print(is so)

print('\n\n')

print(is se)
