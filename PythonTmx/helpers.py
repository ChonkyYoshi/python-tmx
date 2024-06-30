def make_xml_string(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace(">", "&gt;")
        .replace("<", "&lt;")
        .replace("'", "&apos;")
        .replace("'", "&quot;")
    )
