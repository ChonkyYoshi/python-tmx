def escape_for_xml(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace(">", "&gt;")
        .replace("<", "&lt;")
        .replace("'", "&apos;")
        .replace("'", "&quot;")
    )
