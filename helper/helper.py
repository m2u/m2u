import re


def remove_number_suffix(name):
    g = re.match("(.+?)(\d*)$", str(name))
    raw_name = g.group(1)
    return raw_name
