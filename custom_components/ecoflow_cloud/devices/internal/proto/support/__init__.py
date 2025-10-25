def to_lower_camel_case(x: str) -> str:
    result = list[str]()

    upper_next = False

    for c in x:
        if c == "_":
            upper_next = True
        elif upper_next:
            result.append(c.upper())
            upper_next = False
        else:
            result.append(c.lower())
    return "".join(result)

def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
