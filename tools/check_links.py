from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(ROOT.rglob("*.html"))


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ("href", "src"):
            if key in attrs:
                self.refs.append((tag, key, attrs[key]))


def local_target(source, ref):
    parsed = urlparse(ref)

    if parsed.scheme or parsed.netloc or ref.startswith(("mailto:", "tel:", "#")):
        return None

    if parsed.path.startswith("/"):
        raise ValueError("root-relative URL breaks project-site publishing")

    path = unquote(parsed.path)
    if not path:
        return None

    return (source.parent / path).resolve()


def main():
    errors = []

    for html_file in HTML_FILES:
        parser = LinkParser()
        parser.feed(html_file.read_text(encoding="utf-8"))

        for tag, attr, ref in parser.refs:
            try:
                target = local_target(html_file, ref)
            except ValueError as exc:
                errors.append(f"{html_file.relative_to(ROOT)}: {tag} {attr}={ref!r}: {exc}")
                continue

            if target is None:
                continue

            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{html_file.relative_to(ROOT)}: {tag} {attr}={ref!r}: leaves site root")
                continue

            if not target.exists():
                errors.append(f"{html_file.relative_to(ROOT)}: {tag} {attr}={ref!r}: missing local target")

    if errors:
        print("Broken links found:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)

    print(f"Checked {len(HTML_FILES)} HTML files; no broken local links found.")


if __name__ == "__main__":
    main()
