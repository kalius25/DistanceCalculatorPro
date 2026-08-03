"""Privacy-safe production support bundle generation."""

from __future__ import annotations

import json
import os
import platform
import sys
import tempfile
import zipfile
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.logging import SensitiveDataSanitizer


class SupportBundleError(RuntimeError):
    """Raised when a support bundle cannot be created safely."""


@dataclass(frozen=True, slots=True)
class SupportBundlePolicy:
    """Limits and privacy controls applied while collecting artifacts."""

    max_bundle_bytes: int = 25 * 1024 * 1024
    max_source_file_bytes: int = 2 * 1024 * 1024
    max_files: int = 100
    include_html: bool = False
    include_screenshots: bool = False

    def __post_init__(self) -> None:
        if self.max_bundle_bytes < 1:
            raise ValueError("max_bundle_bytes must be at least 1")
        if self.max_source_file_bytes < 1:
            raise ValueError("max_source_file_bytes must be at least 1")
        if self.max_files < 1:
            raise ValueError("max_files must be at least 1")


@dataclass(frozen=True, slots=True)
class SupportBundleEntry:
    """One file included in or skipped from a support bundle."""

    archive_path: str
    source_name: str
    size_bytes: int
    redacted: bool


@dataclass(frozen=True, slots=True)
class SupportBundleResult:
    """Summary returned after a bundle is written successfully."""

    output_path: Path
    included: tuple[SupportBundleEntry, ...]
    skipped: tuple[str, ...]
    bundle_size_bytes: int


class SupportBundleBuilder:
    """Collect diagnostics and create a bounded, privacy-safe ZIP archive."""

    _TEXT_SUFFIXES = frozenset({".json", ".jsonl", ".log", ".txt", ".html"})
    _BINARY_SUFFIXES = frozenset({".png"})

    def __init__(
        self,
        *,
        app_name: str,
        app_version: str,
        log_directory: str | Path = "logs",
        diagnostics_directory: str | Path = "logs/debug",
        policy: SupportBundlePolicy | None = None,
    ) -> None:
        self._app_name = app_name
        self._app_version = app_version
        self._log_directory = Path(log_directory)
        self._diagnostics_directory = Path(diagnostics_directory)
        self._policy = policy or SupportBundlePolicy()

    @property
    def policy(self) -> SupportBundlePolicy:
        return self._policy

    def build(self, output_path: str | Path) -> SupportBundleResult:
        """Create a support archive and atomically replace the target file."""
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        included: list[SupportBundleEntry] = []
        skipped: list[str] = []

        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{destination.stem}.",
            suffix=".tmp",
            dir=destination.parent,
        )
        os.close(descriptor)
        temporary = Path(temporary_name)

        try:
            with zipfile.ZipFile(
                temporary,
                mode="w",
                compression=zipfile.ZIP_DEFLATED,
            ) as archive:
                for source, archive_path in self._candidate_files():
                    if len(included) >= self._policy.max_files:
                        skipped.append(f"{source.name}: file limit reached")
                        break
                    entry = self._add_source(archive, source, archive_path, skipped)
                    if entry is not None:
                        included.append(entry)
                    if temporary.stat().st_size > self._policy.max_bundle_bytes:
                        raise SupportBundleError(
                            "Support bundle exceeded the configured size limit."
                        )

                manifest = self._manifest(included, skipped)
                archive.writestr(
                    "manifest.json",
                    json.dumps(manifest, ensure_ascii=False, indent=2),
                )
                archive.writestr("README.txt", self._readme())

            if temporary.stat().st_size > self._policy.max_bundle_bytes:
                raise SupportBundleError(
                    "Support bundle exceeded the configured size limit."
                )
            os.replace(temporary, destination)
        except SupportBundleError:
            temporary.unlink(missing_ok=True)
            raise
        except (OSError, zipfile.BadZipFile) as error:
            temporary.unlink(missing_ok=True)
            raise SupportBundleError(
                f"Unable to create support bundle: {error}"
            ) from error
        except Exception:
            temporary.unlink(missing_ok=True)
            raise

        return SupportBundleResult(
            output_path=destination,
            included=tuple(included),
            skipped=tuple(skipped),
            bundle_size_bytes=destination.stat().st_size,
        )

    def _candidate_files(self) -> Iterable[tuple[Path, str]]:
        roots = (
            (self._log_directory, "logs"),
            (self._diagnostics_directory, "diagnostics"),
        )
        seen: set[Path] = set()
        candidates: list[tuple[Path, str]] = []
        for root, prefix in roots:
            if not root.exists():
                continue
            for source in root.rglob("*"):
                if not source.is_file():
                    continue
                resolved = source.resolve()
                if resolved in seen:
                    continue
                seen.add(resolved)
                relative = source.relative_to(root).as_posix()
                candidates.append((source, f"{prefix}/{relative}"))
        candidates.sort(key=lambda item: item[0].stat().st_mtime, reverse=True)
        return candidates

    def _add_source(
        self,
        archive: zipfile.ZipFile,
        source: Path,
        archive_path: str,
        skipped: list[str],
    ) -> SupportBundleEntry | None:
        suffix = source.suffix.casefold()
        try:
            size = source.stat().st_size
            if size > self._policy.max_source_file_bytes:
                skipped.append(f"{source.name}: source file too large")
                return None
            if suffix == ".html" and not self._policy.include_html:
                skipped.append(f"{source.name}: HTML excluded by privacy policy")
                return None
            if suffix in self._BINARY_SUFFIXES:
                if not self._policy.include_screenshots:
                    skipped.append(
                        f"{source.name}: screenshot excluded by privacy policy"
                    )
                    return None
                archive.write(source, archive_path)
                return SupportBundleEntry(archive_path, source.name, size, False)
            if suffix not in self._TEXT_SUFFIXES:
                skipped.append(f"{source.name}: unsupported artifact type")
                return None

            text = source.read_text(encoding="utf-8", errors="replace")
            sanitized = self._sanitize_text(text)
            archive.writestr(archive_path, sanitized)
            return SupportBundleEntry(
                archive_path=archive_path,
                source_name=source.name,
                size_bytes=len(sanitized.encode("utf-8")),
                redacted=sanitized != text,
            )
        except OSError as error:
            skipped.append(f"{source.name}: unavailable ({error})")
            return None

    @staticmethod
    def _sanitize_text(text: str) -> str:
        return "\n".join(
            str(SensitiveDataSanitizer.sanitize(line)) for line in text.splitlines()
        )

    def _manifest(
        self,
        included: list[SupportBundleEntry],
        skipped: list[str],
    ) -> dict[str, object]:
        return {
            "bundle_version": 1,
            "created_at": datetime.now(UTC).isoformat(),
            "application": {
                "name": self._app_name,
                "version": self._app_version,
            },
            "environment": {
                "platform": platform.platform(),
                "python": platform.python_version(),
                "implementation": platform.python_implementation(),
                "executable_name": Path(sys.executable).name,
            },
            "privacy": {
                "workbook_included": False,
                "html_included": self._policy.include_html,
                "screenshots_included": self._policy.include_screenshots,
                "text_redaction_enabled": True,
            },
            "included": [asdict(entry) for entry in included],
            "skipped": skipped,
        }

    def _readme(self) -> str:
        return (
            f"{self._app_name} support bundle\n"
            f"Application version: {self._app_version}\n\n"
            "This archive intentionally excludes source workbooks, credentials, "
            "cookies and raw route coordinates. Text artifacts are sanitized "
            "before inclusion. Screenshots and HTML are excluded by default.\n"
        )


__all__ = [
    "SupportBundleBuilder",
    "SupportBundleEntry",
    "SupportBundleError",
    "SupportBundlePolicy",
    "SupportBundleResult",
]
