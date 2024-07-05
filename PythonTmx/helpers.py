def xml_escape(value: str) -> str:
    """
    simple helper to xml escape strings
    """
    return (
        value.replace("&", "&amp;")
        .replace(">", "&gt;")
        .replace("<", "&lt;")
        .replace("'", "&apos;")
        .replace('"', "&quot;")
    )
