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
