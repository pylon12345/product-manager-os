#!/usr/bin/env python3
"""Opt-in, exact-URL public-source sync and local SQLite backup for PM OS.

The CLI deliberately has no scheduler. A user or Codex automation invokes it
with an explicit data directory and a reviewed source allowlist.
"""

from __future__ import annotations

import argparse
from contextlib import closing, contextmanager
import hashlib
from html.parser import HTMLParser
import ipaddress
import json
import os
from pathlib import Path
import re
import shutil
import socket
import sqlite3
import sys
import time
from datetime import datetime, timezone
from urllib import error, parse, request, robotparser
from uuid import uuid4


SCHEMA_VERSION = 1
DB_NAME = "knowledge.sqlite3"
USER_AGENT = "ProductManagerOS-KB/1.0 (+local-public-source-archive)"
ROBOTS_AGENT = "ProductManagerOS-KB"
TIMEOUT_SECONDS = 12
MAX_PAGE_BYTES = 1_500_000
MAX_ROBOTS_BYTES = 256_000
MAX_REQUEST_SECONDS = 45
BACKUP_WARNING_BYTES = 1024 * 1024 * 1024
MIN_REQUEST_INTERVAL = 1.0
MIN_TEXT_CHARS = 100
MAX_TEXT_CHARS = 300_000


class KBError(Exception):
    """An expected, user-readable knowledge-base error."""


@contextmanager
def mutation_lock(data_dir: Path):
    """OS lock for one CLI writer per data directory; survives process crashes."""
    data_dir.mkdir(parents=True, exist_ok=True)
    lock_path = data_dir / ".pm-kb-write.lock"
    with lock_path.open("a+b") as stream:
        if lock_path.stat().st_size == 0:
            stream.write(b"\0")
            stream.flush()
        stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise KBError("knowledge base is busy with another sync, backup, or restore") from exc
        try:
            yield
        finally:
            stream.seek(0)
            if os.name == "nt":
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def emit(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, sort_keys=True))


def require_data_dir(value: str) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        raise KBError("--data-dir must be an explicit absolute path")
    path = path.resolve()
    if path == Path(path.anchor):
        raise KBError("--data-dir cannot be a filesystem root")
    return path


def validate_url(url: object) -> str:
    if not isinstance(url, str) or not url:
        raise KBError("source URL must be a nonempty HTTPS string")
    parts = parse.urlsplit(url)
    if parts.scheme != "https" or not parts.hostname:
        raise KBError("source URL must use HTTPS")
    if parts.username or parts.password or parts.query or parts.fragment:
        raise KBError("source URLs cannot contain credentials, queries, or fragments")
    if parts.port not in (None, 443):
        raise KBError("source URL must use the standard HTTPS port")
    hostname = parts.hostname.lower()
    if hostname == "localhost" or hostname.endswith(".local"):
        raise KBError("local network hosts are not allowed as public sources")
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        raise KBError("IP literals are not allowed as public sources")
    return url


def load_sources(path: Path) -> list[dict[str, object]]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise KBError(f"Cannot read source allowlist: {type(exc).__name__}") from exc
    if not isinstance(document, dict) or document.get("version") != 1:
        raise KBError("source allowlist needs version: 1")
    sources = document.get("sources")
    if not isinstance(sources, list) or not sources:
        raise KBError("source allowlist needs a nonempty sources array")
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()
    for item in sources:
        if not isinstance(item, dict):
            raise KBError("every source must be an object")
        source_id = item.get("id")
        if not isinstance(source_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", source_id):
            raise KBError("source id must be lowercase letters, digits, hyphens, or underscores")
        if source_id in seen_ids:
            raise KBError(f"duplicate source id: {source_id}")
        seen_ids.add(source_id)
        url = validate_url(item.get("url"))
        if url in seen_urls:
            raise KBError("duplicate source URL in allowlist")
        seen_urls.add(url)
        for field in ("title", "topic"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise KBError(f"source {source_id}: {field} must be nonempty text")
        if not isinstance(item.get("enabled"), bool):
            raise KBError(f"source {source_id}: enabled must be true or false")
    return sources


def connect_db(path: Path, *, create: bool = False) -> sqlite3.Connection:
    if create:
        path.parent.mkdir(parents=True, exist_ok=True)
        new_database = not path.exists()
        conn = sqlite3.connect(path)
    else:
        if not path.is_file():
            raise KBError(f"knowledge database not found: {path}")
        conn = sqlite3.connect(f"{path.as_uri()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    if create and new_database:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sources (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                topic TEXT NOT NULL,
                enabled INTEGER NOT NULL,
                last_checked_at TEXT,
                last_status TEXT,
                last_error TEXT,
                etag TEXT,
                last_modified TEXT,
                latest_snapshot_id INTEGER
            );
            CREATE TABLE IF NOT EXISTS snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL REFERENCES sources(id),
                fetched_at TEXT NOT NULL,
                url TEXT NOT NULL,
                title TEXT NOT NULL,
                content_text TEXT NOT NULL,
                content_sha256 TEXT NOT NULL,
                http_status INTEGER NOT NULL,
                etag TEXT,
                last_modified TEXT,
                bytes_read INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS snapshots_source_time
                ON snapshots(source_id, fetched_at DESC);
            """
        )
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO metadata(key, value) VALUES ('schema_version', ?)",
                (str(SCHEMA_VERSION),),
            )
    try:
        version_row = conn.execute("SELECT value FROM metadata WHERE key='schema_version'").fetchone()
    except sqlite3.Error as exc:
        conn.close()
        raise KBError("existing database is not a PM knowledge database") from exc
    if version_row is None or version_row[0] != str(SCHEMA_VERSION):
        conn.close()
        raise KBError("unsupported knowledge database schema version")
    return conn


def verify_database(path: Path) -> dict[str, object]:
    with closing(connect_db(path)) as conn:
        integrity = [row[0] for row in conn.execute("PRAGMA integrity_check")]
        if integrity != ["ok"]:
            raise KBError("SQLite integrity check failed")
        if conn.execute("PRAGMA foreign_key_check").fetchone() is not None:
            raise KBError("SQLite foreign-key check failed")
        source_count = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
        snapshots = conn.execute(
            "SELECT id, content_text, content_sha256 FROM snapshots"
        )
        snapshot_count = 0
        for row in snapshots:
            expected = hashlib.sha256(row["content_text"].encode("utf-8")).hexdigest()
            if expected != row["content_sha256"]:
                raise KBError(f"snapshot content hash mismatch: {row['id']}")
            snapshot_count += 1
        if conn.execute(
            "SELECT 1 FROM sources AS s LEFT JOIN snapshots AS v "
            "ON s.latest_snapshot_id=v.id AND s.id=v.source_id "
            "WHERE s.latest_snapshot_id IS NOT NULL AND v.id IS NULL LIMIT 1"
        ).fetchone() is not None:
            raise KBError("invalid latest snapshot reference")
    return {"sources": source_count, "snapshots": snapshot_count}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def verify_backup(path: Path) -> dict[str, object]:
    if not path.is_file():
        raise KBError(f"backup not found: {path}")
    details = verify_database(path)
    sidecar = Path(f"{path}.sha256")
    if not sidecar.is_file():
        raise KBError("backup checksum sidecar is missing")
    try:
        stored = sidecar.read_text(encoding="ascii").split()[0]
    except (OSError, UnicodeError, IndexError) as exc:
        raise KBError("backup checksum sidecar is unreadable") from exc
    actual = sha256_file(path)
    if stored != actual:
        raise KBError("backup file checksum mismatch")
    details["file_sha256"] = actual
    details["checksum_sidecar"] = "verified"
    return details


def create_backup(data_dir: Path, *, prefix: str = "pm-kb") -> Path:
    db_path = data_dir / DB_NAME
    verify_database(db_path)
    backup_dir = data_dir / "backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = backup_dir / f"{prefix}-{stamp}-{uuid4().hex[:8]}.sqlite3"
    temporary = backup_dir / f".{target.name}.tmp"
    try:
        with closing(sqlite3.connect(db_path)) as source:
            with closing(sqlite3.connect(temporary)) as destination:
                source.backup(destination)
        verify_database(temporary)
        os.replace(temporary, target)
        digest = sha256_file(target)
        checksum = Path(f"{target}.sha256")
        checksum.write_text(f"{digest}  {target.name}\n", encoding="ascii")
        verify_backup(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def restore_backup(data_dir: Path, backup_path: Path, *, force: bool) -> dict[str, object]:
    backup_path = backup_path.resolve()
    target = data_dir / DB_NAME
    if backup_path == target:
        raise KBError("backup file and live database cannot be the same path")
    details = verify_backup(backup_path)
    safety_backup: Path | None = None
    raw_quarantine: Path | None = None
    if target.exists() and not force:
        raise KBError("live database exists; use restore --force to back it up and replace it")
    data_dir.mkdir(parents=True, exist_ok=True)
    if target.exists():
        # Capture raw files before even attempting SQLite verification: opening
        # a damaged WAL database can itself recreate or modify its SHM file.
        raw_quarantine = preserve_raw_database(data_dir)
        try:
            verify_database(target)
        except (KBError, sqlite3.Error):
            # Recovery must work when the active DB is corrupt. Preserve exact
            # raw files first; they are NOT a verified/usable SQLite backup.
            temporary = data_dir / f".{DB_NAME}.{uuid4().hex[:8]}.restore-tmp"
            try:
                shutil.copyfile(backup_path, temporary)
                verify_database(temporary)
                for suffix in ("-wal", "-shm"):
                    companion = data_dir / f"{DB_NAME}{suffix}"
                    if companion.exists():
                        os.replace(companion, raw_quarantine / f"{companion.name}.detached")
                os.replace(temporary, target)
                verify_database(target)
            except (KBError, sqlite3.Error, OSError) as exc:
                raise KBError(
                    f"restore failed; original raw files were preserved at {raw_quarantine}"
                ) from exc
            finally:
                temporary.unlink(missing_ok=True)
        else:
            safety_backup = create_backup(data_dir, prefix="pre-restore")
            # Use SQLite's backup API for an existing healthy destination.
            # Replacing only its main file could conflict with WAL/SHM.
            with closing(sqlite3.connect(f"{backup_path.as_uri()}?mode=ro", uri=True)) as source:
                with closing(sqlite3.connect(target)) as destination:
                    source.backup(destination)
            verify_database(target)
    else:
        temporary = data_dir / f".{DB_NAME}.{uuid4().hex[:8]}.restore-tmp"
        try:
            shutil.copyfile(backup_path, temporary)
            verify_database(temporary)
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
    return {
        "status": "restored",
        "database": str(target),
        "from_backup": str(backup_path),
        "pre_restore_backup": str(safety_backup) if safety_backup else None,
        "raw_original_quarantine": str(raw_quarantine) if raw_quarantine else None,
        "raw_original_verified": False if raw_quarantine else None,
        "verified": details,
    }


def preserve_raw_database(data_dir: Path) -> Path:
    """Keep byte-for-byte copies of a damaged DB and companions before restore."""
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = data_dir / "quarantine" / f"pre-restore-raw-{stamp}-{uuid4().hex[:8]}"
    destination.mkdir(parents=True, exist_ok=False)
    files = [data_dir / DB_NAME,
             data_dir / f"{DB_NAME}-wal",
             data_dir / f"{DB_NAME}-shm"]
    copied: list[dict[str, object]] = []
    try:
        for source in files:
            if not source.is_file():
                continue
            target = destination / source.name
            shutil.copy2(source, target)
            original_hash = sha256_file(source)
            if sha256_file(target) != original_hash:
                raise KBError("raw quarantine copy failed checksum verification")
            copied.append({"name": source.name, "bytes": target.stat().st_size,
                           "sha256": original_hash})
        if not copied or copied[0]["name"] != DB_NAME:
            raise KBError("damaged live database could not be copied")
        (destination / "manifest.json").write_text(
            json.dumps({"captured_at": utc_now(), "verified_sqlite": False,
                        "files": copied}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except (OSError, KBError) as exc:
        raise KBError(f"cannot safely preserve damaged live database at {destination}") from exc
    return destination


class NoRedirectHandler(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        raise KBError("redirect blocked; review and update the exact source URL")


def resolve_addresses(hostname: str) -> list[str]:
    """Resolve all A/AAAA answers for fail-closed public-address preflight."""
    return [entry[4][0] for entry in socket.getaddrinfo(
        hostname, 443, type=socket.SOCK_STREAM
    )]


class Fetcher:
    def __init__(self, *, opener=None, clock=time.monotonic, sleeper=time.sleep,
                 resolver=None):
        self.opener = opener or request.build_opener(NoRedirectHandler)
        self.clock = clock
        self.sleeper = sleeper
        self.resolver = resolver or resolve_addresses
        self.last_call: dict[str, float] = {}
        self.robots_cache: dict[str, robotparser.RobotFileParser | None] = {}

    def _request(self, url: str, headers: dict[str, str], limit: int, interval: float):
        parts = parse.urlsplit(url)
        self._check_public_destination(parts.hostname)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin in self.last_call:
            remaining = interval - (self.clock() - self.last_call[origin])
            if remaining > 0:
                self.sleeper(remaining)
        self.last_call[origin] = self.clock()
        req = request.Request(url, headers={"User-Agent": USER_AGENT, **headers})
        try:
            with self.opener.open(req, timeout=TIMEOUT_SECONDS) as response:
                status = response.getcode()
                deadline = self.clock() + MAX_REQUEST_SECONDS
                chunks: list[bytes] = []
                size = 0
                read = getattr(response, "read1", response.read)
                while True:
                    if self.clock() >= deadline:
                        raise KBError("response exceeded total read time limit")
                    chunk = read(min(64 * 1024, limit + 1 - size))
                    if not chunk:
                        break
                    chunks.append(chunk)
                    size += len(chunk)
                    if size > limit:
                        raise KBError(f"response exceeds {limit} byte limit")
                return status, b"".join(chunks), response.headers
        except error.HTTPError as exc:
            if exc.code == 304:
                return 304, b"", exc.headers
            if exc.code == 404 and parts.path == "/robots.txt":
                return 404, b"", exc.headers
            raise KBError(f"HTTP {exc.code} from approved source") from exc
        except (error.URLError, TimeoutError, OSError) as exc:
            raise KBError(f"network request failed: {type(exc).__name__}") from exc

    def _check_public_destination(self, hostname: str | None) -> None:
        if not hostname:
            raise KBError("destination hostname is missing")
        try:
            addresses = self.resolver(hostname)
        except (OSError, ValueError) as exc:
            raise KBError("DNS preflight failed; skipped") from exc
        if not addresses:
            raise KBError("DNS preflight returned no addresses; skipped")
        try:
            public = all(ipaddress.ip_address(address).is_global for address in addresses)
        except ValueError as exc:
            raise KBError("DNS preflight returned an invalid address; skipped") from exc
        if not public:
            raise KBError("DNS preflight found a non-public address; skipped")

    def allowed(self, url: str) -> tuple[bool, float]:
        parts = parse.urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        if origin not in self.robots_cache:
            robots_url = f"{origin}/robots.txt"
            status, body, _ = self._request(
                robots_url, {}, MAX_ROBOTS_BYTES, MIN_REQUEST_INTERVAL
            )
            if status == 404:
                # A definitive 404 means there are no published robots rules.
                self.robots_cache[origin] = None
            elif status == 200:
                parser = robotparser.RobotFileParser()
                parser.set_url(robots_url)
                parser.parse(body.decode("utf-8-sig", errors="replace").splitlines())
                self.robots_cache[origin] = parser
            else:
                raise KBError(f"robots.txt returned unexpected HTTP {status}; skipped")
        parser = self.robots_cache[origin]
        if parser is None:
            return True, MIN_REQUEST_INTERVAL
        delay = parser.crawl_delay(ROBOTS_AGENT) or MIN_REQUEST_INTERVAL
        if delay > 120:
            raise KBError("robots.txt crawl-delay exceeds 120 seconds; skipped")
        return parser.can_fetch(ROBOTS_AGENT, url), max(float(delay), MIN_REQUEST_INTERVAL)

    def page(self, url: str, *, etag: str | None, modified: str | None, interval: float):
        headers = {"Accept": "text/html, text/plain;q=0.8"}
        if etag:
            headers["If-None-Match"] = etag
        if modified:
            headers["If-Modified-Since"] = modified
        return self._request(url, headers, MAX_PAGE_BYTES, interval)


BLOCK_TAGS = {
    "address", "article", "blockquote", "br", "dd", "div", "dl", "dt",
    "h1", "h2", "h3", "h4", "h5", "h6", "hr", "li", "main", "ol", "p",
    "pre", "section", "table", "td", "th", "tr", "ul",
}
SKIP_TAGS = {"script", "style", "noscript", "nav", "header", "footer", "aside", "form", "svg"}


class ReadableText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.skip_depth = 0
        self.main_depth = 0
        self.title_depth = 0
        self.all_parts: list[str] = []
        self.main_parts: list[str] = []
        self.title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag in SKIP_TAGS:
            self.skip_depth += 1
        if tag in ("main", "article"):
            self.main_depth += 1
        if tag == "title":
            self.title_depth += 1
        if tag in BLOCK_TAGS and not self.skip_depth:
            self.all_parts.append("\n")
            if self.main_depth:
                self.main_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in BLOCK_TAGS and not self.skip_depth:
            self.all_parts.append("\n")
            if self.main_depth:
                self.main_parts.append("\n")
        if tag in SKIP_TAGS and self.skip_depth:
            self.skip_depth -= 1
        if tag in ("main", "article") and self.main_depth:
            self.main_depth -= 1
        if tag == "title" and self.title_depth:
            self.title_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.title_depth:
            self.title_parts.append(data)
        if self.skip_depth:
            return
        if data.strip():
            self.all_parts.append(data)
            if self.main_depth:
                self.main_parts.append(data)


def normalize_text(parts: list[str]) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in " ".join(parts).splitlines()]
    return "\n".join(line for line in lines if line)[:MAX_TEXT_CHARS]


def extract_text(body: bytes, content_type: str, fallback_title: str) -> tuple[str, str]:
    mime = content_type.split(";", 1)[0].strip().lower()
    if mime not in ("text/html", "application/xhtml+xml", "text/plain"):
        raise KBError(f"unsupported content type: {mime or 'missing'}")
    charset_match = re.search(r"charset\s*=\s*['\"]?([\w.-]+)", content_type, re.I)
    encoding = charset_match.group(1) if charset_match else "utf-8"
    try:
        decoded = body.decode(encoding, errors="replace")
    except LookupError as exc:
        raise KBError("unsupported page character encoding") from exc
    if mime == "text/plain":
        text = normalize_text([decoded])
        title = fallback_title
    else:
        reader = ReadableText()
        reader.feed(decoded)
        main_text = normalize_text(reader.main_parts)
        text = main_text if len(main_text) >= MIN_TEXT_CHARS else normalize_text(reader.all_parts)
        title = " ".join(reader.title_parts).strip() or fallback_title
    if len(text) < MIN_TEXT_CHARS:
        raise KBError("page has insufficient readable text; no snapshot saved")
    return title[:300], text


def record_source(conn: sqlite3.Connection, source: dict[str, object]) -> sqlite3.Row:
    source_id = str(source["id"])
    existing = conn.execute("SELECT * FROM sources WHERE id=?", (source_id,)).fetchone()
    with conn:
        if existing is None:
            conn.execute(
                "INSERT INTO sources(id,title,url,topic,enabled) VALUES (?,?,?,?,?)",
                (source_id, source["title"], source["url"], source["topic"], int(source["enabled"])),
            )
        else:
            url_changed = existing["url"] != source["url"]
            conn.execute(
                "UPDATE sources SET title=?,url=?,topic=?,enabled=?,"
                "etag=CASE WHEN ? THEN NULL ELSE etag END,"
                "last_modified=CASE WHEN ? THEN NULL ELSE last_modified END "
                "WHERE id=?",
                (source["title"], source["url"], source["topic"],
                 int(source["enabled"]), url_changed, url_changed, source_id),
            )
    return conn.execute("SELECT * FROM sources WHERE id=?", (source_id,)).fetchone()


def sync_one(conn: sqlite3.Connection, source: dict[str, object], fetcher: Fetcher) -> dict[str, object]:
    row = record_source(conn, source)
    source_id = str(source["id"])
    url = str(source["url"])
    if not source["enabled"]:
        return {"id": source_id, "status": "disabled"}
    checked_at = utc_now()
    try:
        allowed, interval = fetcher.allowed(url)
        if not allowed:
            raise KBError("robots.txt disallows this URL; skipped")
        status, body, headers = fetcher.page(
            url, etag=row["etag"], modified=row["last_modified"], interval=interval
        )
        if status == 304:
            latest_for_304 = None
            if row["latest_snapshot_id"] is not None:
                latest_for_304 = conn.execute(
                    "SELECT url FROM snapshots WHERE id=?", (row["latest_snapshot_id"],)
                ).fetchone()
            if latest_for_304 is None or latest_for_304["url"] != url:
                raise KBError("server returned 304 without a local snapshot")
            with conn:
                conn.execute(
                    "UPDATE sources SET last_checked_at=?,last_status=?,last_error=NULL WHERE id=?",
                    (checked_at, "not_modified", source_id),
                )
            return {"id": source_id, "status": "not_modified", "snapshot_id": row["latest_snapshot_id"]}
        if status != 200:
            raise KBError(f"unexpected HTTP {status}; no snapshot saved")
        title, text = extract_text(body, headers.get("Content-Type", ""), str(source["title"]))
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        etag = headers.get("ETag")
        modified = headers.get("Last-Modified")
        latest = None
        if row["latest_snapshot_id"] is not None:
            latest = conn.execute(
                "SELECT content_sha256,url FROM snapshots WHERE id=?", (row["latest_snapshot_id"],)
            ).fetchone()
        if latest is not None and latest["content_sha256"] == digest and latest["url"] == url:
            with conn:
                conn.execute(
                    "UPDATE sources SET last_checked_at=?,last_status=?,last_error=NULL,etag=?,last_modified=? WHERE id=?",
                    (checked_at, "unchanged", etag, modified, source_id),
                )
            return {"id": source_id, "status": "unchanged", "snapshot_id": row["latest_snapshot_id"]}
        with conn:
            cursor = conn.execute(
                "INSERT INTO snapshots(source_id,fetched_at,url,title,content_text,content_sha256,"
                "http_status,etag,last_modified,bytes_read) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (source_id, checked_at, url, title, text, digest, 200, etag, modified, len(body)),
            )
            snapshot_id = cursor.lastrowid
            conn.execute(
                "UPDATE sources SET last_checked_at=?,last_status=?,last_error=NULL,etag=?,last_modified=?,"
                "latest_snapshot_id=? WHERE id=?",
                (checked_at, "new", etag, modified, snapshot_id, source_id),
            )
        return {"id": source_id, "status": "new", "snapshot_id": snapshot_id, "sha256": digest}
    except KBError as exc:
        with conn:
            conn.execute(
                "UPDATE sources SET last_checked_at=?,last_status='error',last_error=? WHERE id=?",
                (checked_at, str(exc), source_id),
            )
        return {"id": source_id, "status": "error", "error": str(exc)}


def sync_sources(data_dir: Path, source_file: Path, *, source_id: str | None = None,
                 fetcher: Fetcher | None = None) -> dict[str, object]:
    sources = load_sources(source_file)
    full_sync = source_id is None
    if source_id is not None:
        sources = [source for source in sources if source["id"] == source_id]
        if not sources:
            raise KBError(f"source id not in allowlist: {source_id}")
    fetcher = fetcher or Fetcher()
    with closing(connect_db(data_dir / DB_NAME, create=True)) as conn:
        if full_sync:
            current_ids = {str(source["id"]) for source in sources}
            with conn:
                for row in conn.execute("SELECT id FROM sources"):
                    if row["id"] not in current_ids:
                        conn.execute(
                            "UPDATE sources SET enabled=0,last_status='retired',last_error=NULL WHERE id=?",
                            (row["id"],),
                        )
        results = [sync_one(conn, source, fetcher) for source in sources]
    failed = sum(result["status"] == "error" for result in results)
    return {
        "status": "partial_failure" if failed else "ok",
        "database": str(data_dir / DB_NAME),
        "source_file": str(source_file.resolve()),
        "total": len(results),
        "failed": failed,
        "results": results,
    }


def storage_report(data_dir: Path) -> dict[str, object]:
    db_path = data_dir / DB_NAME
    wal_path = data_dir / f"{DB_NAME}-wal"
    backup_dir = data_dir / "backups"
    backups = list(backup_dir.glob("*.sqlite3")) if backup_dir.is_dir() else []
    backup_bytes = sum(path.stat().st_size for path in backups if path.is_file())
    quarantine_dir = data_dir / "quarantine"
    quarantines = [path for path in quarantine_dir.iterdir() if path.is_dir()] \
        if quarantine_dir.is_dir() else []
    quarantine_bytes = sum(
        file.stat().st_size for directory in quarantines for file in directory.iterdir()
        if file.is_file()
    )
    return {
        "database_bytes": db_path.stat().st_size if db_path.is_file() else 0,
        "database_wal_bytes": wal_path.stat().st_size if wal_path.is_file() else 0,
        "backup_count": len([path for path in backups if path.is_file()]),
        "backup_bytes": backup_bytes,
        "backup_size_warning": backup_bytes >= BACKUP_WARNING_BYTES,
        "quarantine_count": len(quarantines),
        "quarantine_bytes": quarantine_bytes,
    }


def status_report(data_dir: Path) -> dict[str, object]:
    db_path = data_dir / DB_NAME
    if not db_path.exists():
        return {"status": "not_initialized", "database": str(db_path),
                "sources": [], "storage": storage_report(data_dir)}
    with closing(connect_db(db_path)) as conn:
        rows = conn.execute(
            "SELECT s.id,s.title,s.url,s.topic,s.enabled,s.last_checked_at,s.last_status,"
            "s.last_error,s.latest_snapshot_id,v.fetched_at AS snapshot_at,"
            "v.url AS snapshot_url,"
            "v.content_sha256 AS snapshot_sha256,"
            "(SELECT COUNT(*) FROM snapshots WHERE source_id=s.id) AS versions "
            "FROM sources AS s LEFT JOIN snapshots AS v ON v.id=s.latest_snapshot_id ORDER BY s.id"
        ).fetchall()
        sources = [dict(row) for row in rows]
        total = conn.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
    return {"status": "ok", "database": str(db_path), "snapshots": total,
            "sources": sources, "storage": storage_report(data_dir)}


def search_db(data_dir: Path, query: str, *, limit: int) -> dict[str, object]:
    query = query.strip()
    if not query:
        raise KBError("search query cannot be empty")
    if not 1 <= limit <= 100:
        raise KBError("--limit must be between 1 and 100")
    with closing(connect_db(data_dir / DB_NAME)) as conn:
        rows = conn.execute(
            "SELECT s.id AS source_id,s.topic,v.url,v.title,v.fetched_at,v.content_text,"
            "v.content_sha256 FROM sources AS s JOIN snapshots AS v ON v.id=s.latest_snapshot_id "
            "ORDER BY s.id"
        ).fetchall()
    matches: list[dict[str, object]] = []
    needle = query.casefold()
    for row in rows:
        text = row["content_text"]
        index = text.casefold().find(needle)
        if index < 0 and needle not in row["title"].casefold():
            continue
        start = max(0, index - 100) if index >= 0 else 0
        excerpt = text[start:start + 300].replace("\n", " ")
        matches.append({
            "source_id": row["source_id"], "topic": row["topic"], "url": row["url"],
            "title": row["title"], "fetched_at": row["fetched_at"],
            "content_sha256": row["content_sha256"], "excerpt": excerpt,
        })
        if len(matches) >= limit:
            break
    return {"query": query, "count": len(matches), "results": matches}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, help="explicit absolute local KB directory")
    parser.add_argument("--sources-file", type=Path, help="reviewed JSON exact-URL allowlist")
    commands = parser.add_subparsers(dest="command", required=True)
    sync = commands.add_parser("sync", help="fetch enabled public pages once")
    sync.add_argument("--source", help="sync one allowlisted source id")
    search = commands.add_parser("search", help="search latest offline snapshots")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    commands.add_parser("status", help="show local source and snapshot status")
    commands.add_parser("backup", help="create and verify timestamped SQLite backup")
    verify = commands.add_parser("verify-backup", help="verify backup integrity and hashes")
    verify.add_argument("backup_file", type=Path)
    restore = commands.add_parser("restore", help="restore an explicitly selected backup")
    restore.add_argument("backup_file", type=Path)
    restore.add_argument("--force", action="store_true", help="pre-backup and replace existing live DB")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        data_dir = require_data_dir(args.data_dir)
        if args.command == "sync":
            if args.sources_file is None:
                raise KBError("sync requires --sources-file")
            with mutation_lock(data_dir):
                report = sync_sources(data_dir, args.sources_file, source_id=args.source)
            emit(report)
            return 1 if report["failed"] else 0
        if args.command == "search":
            emit(search_db(data_dir, args.query, limit=args.limit))
        elif args.command == "status":
            emit(status_report(data_dir))
        elif args.command == "backup":
            with mutation_lock(data_dir):
                path = create_backup(data_dir)
            emit({"status": "ok", "backup": str(path), "verified": verify_backup(path)})
        elif args.command == "verify-backup":
            emit({"status": "ok", "backup": str(args.backup_file.resolve()),
                  "verified": verify_backup(args.backup_file.resolve())})
        elif args.command == "restore":
            with mutation_lock(data_dir):
                emit(restore_backup(data_dir, args.backup_file, force=args.force))
        return 0
    except (KBError, sqlite3.Error, OSError) as exc:
        # Expected errors are structured for unattended weekly runs. Do not
        # print exception reprs or page content, which could expose secrets.
        message = str(exc) if isinstance(exc, KBError) else type(exc).__name__
        emit({"status": "error", "error": message})
        return 2


if __name__ == "__main__":
    sys.exit(main())
