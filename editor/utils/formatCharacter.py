def buildChar(name, description, personality, motivation, image_mime_type, note=""):
    resp = f"**Character: {name}**\n\n"
    if image_mime_type:
        resp = f"{resp}This picture shows **{name}**\n\n"

    if description != "":
        resp = f"{resp}**Description:** {description}\n\n"

    if personality != "":
        resp = f"{resp}**Personality:** {personality}\n\n"

    if motivation != "":
        resp = f"{resp}**Motivation:** {motivation}\n\n"

    if note != "":
        resp = f"{resp}**Note:** {note}\n\n"

    return resp