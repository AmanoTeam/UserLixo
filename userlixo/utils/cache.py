from datetime import UTC, datetime
from pathlib import Path


def clean_cache():
    for file in Path("cache/").glob("*"):
        if not Path(file).is_file():
            continue
        creation_time = datetime.fromtimestamp(
            Path(file).stat().st_ctime,
            tz=UTC,
        )
        now_time = datetime.now(tz=UTC)
        diff = now_time - creation_time
        minutes_passed = diff.total_seconds() / 60

        if minutes_passed >= 10:
            Path(file).unlink()
