from commons import BINARY_PATH


def ensure_stockfish_binary():
    import shutil
    import subprocess
    import tarfile
    from io import BytesIO

    import requests

    if BINARY_PATH.exists():
        return

    BINARY_PATH.parent.mkdir(exist_ok=True)

    try:
        response = requests.get(
            "https://github.com/official-stockfish/Stockfish/archive/refs/heads/master.tar.gz",
            timeout=30,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to download Stockfish source: {e}") from e

    data = response.content
    buffer = BytesIO(data)
    _ = buffer.seek(0)

    try:
        with tarfile.open(fileobj=buffer) as tar:
            tar.extractall(path=BINARY_PATH.parent, filter="data")
    except tarfile.TarError as e:
        raise RuntimeError(f"Failed to extract Stockfish tarball: {e}") from e

    src = BINARY_PATH.parent / "Stockfish-master/src"
    try:
        _ = subprocess.run(
            ["make", "-j", "profile-build"],
            cwd=src,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to compile Stockfish:\nstdout:\n{e.stdout}\nstderr:\n{e.stderr}"
        ) from e

    _ = (src / "stockfish").replace(BINARY_PATH)
    shutil.rmtree(BINARY_PATH.parent / "Stockfish-sf_18", ignore_errors=True)
