"""Transform a viewer CSP for WordCraft print frames."""
import re


def with_wordcraft_print_policy(block):
    """Split the existing CSP into mutually exclusive matchers; widen frame-src only.

    Refuse unfamiliar/already customized policies instead of silently overwriting
    another operator's change. Rollback restores the complete original file.
    """
    policy = re.compile(r'(?m)^(\s*)header (?:(@otherDocuments) )?>Content-Security-Policy "([^"\n]+)"$')
    matches = list(policy.finditer(block))
    assert len(matches) == 1 and '@wordcraft_print' not in block and '@other_viewer' not in block
    match = matches[0]
    base = match.group(3)
    weather = bool(match.group(2))
    if weather:
        assert re.search(r"(?m)^\s*@otherDocuments not path / /index\.html$", block)
    assert base.count("frame-src 'self';") == 1 and "object-src 'none';" in base
    printing = base.replace("frame-src 'self';", "frame-src 'self' blob:;")
    indent = match.group(1)
    lines = [
        '@wordcraft_print path /wordcraft/index.html',
        '@other_viewer not path /wordcraft/index.html' + (' / /index.html' if weather else ''),
        'header @other_viewer >Content-Security-Policy "' + base + '"',
        'header @wordcraft_print >Content-Security-Policy "' + printing + '"',
    ]
    return block[:match.start()] + ('\n'.join(indent + line for line in lines)) + block[match.end():]
