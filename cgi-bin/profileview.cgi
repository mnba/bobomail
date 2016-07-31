#!/usr/bin/env python
from bobomailrc import profile_stats

import pstats
print("Content-type: text/plain\n\n")

p=pstats.Stats(profile_stats)

items_to_print=10

print("TIME----------------------------------\n")
p.sort_stats('time').print_stats(items_to_print)
print("CALLERS-------------------------------\n")
p.print_callers(items_to_print)
print("CUMULATIVE----------------------------\n")
p.sort_stats('cumulative').print_stats(items_to_print)
