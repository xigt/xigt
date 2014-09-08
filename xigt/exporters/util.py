import re

def sub(s, tier_type, subs):
    for tier_regex, patterns in subs:
        if not re.match(tier_regex, tier_type):
            continue
        for regex, sub_pattern in patterns:
            if isinstance(sub_pattern, str):
                s = re.sub(regex, sub_pattern, s)
            elif len(sub_pattern) == 2:
                f = eval('lambda {}: {}'.format(*sub_pattern))
                s = re.sub(regex, f, s)
    return s