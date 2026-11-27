"""Arranca o Chrome com remote debugging, em Windows, macOS e Linux.

Substitui o antigo `start_chrome_debug.bat`. Os scrapers que precisam de um
browser real (Indeed e keywords do LinkedIn) ligam-se a este Chrome através de
`http://localhost:9222` (CDP).

Uso:
    python start_chrome_debug.py            # arranca em 9222
    python start_chrome_debug.py --check    # só verifica se já está a correr
    python start_chrome_debug.py --port 9333
    python start_chrome_debug.py --chrome-path "/caminho/para/chrome"

O perfil fica em `chrome-profile/` na raiz do repositório, para reutilizar
cookies e sessão entre execuções (Login do LinkedIn, por exemplo).
"""

from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROFILE_DIR = REPO_ROOT / "chrome-profile"
DEFAULT_PORT = 9222


def port_is_open(port: int, host: str = "127.0.0.1", timeout: float = 0.5) -> bool:
    """Devolve True se algo estiver a escutar na porta indicada."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        return sock.connect_ex((host, port)) == 0


def _windows_candidates() -> list[str]:
    candidates: list[str] = []

    # Registo: é a forma mais fiável de encontrar o Chrome no Windows.
    try:
        import winreg
    except ImportError:  # não estamos no Windows
        winreg = None  # type: ignore[assignment]

    if winreg is not None:
        key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe"
        views = (winreg.KEY_WOW64_64KEY, winreg.KEY_WOW64_32KEY)
        for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
            for view in views:
                try:
                    with winreg.OpenKey(hive, key, 0, winreg.KEY_READ | view) as handle:
                        candidates.append(winreg.QueryValue(handle, None))
                except OSError:
                    continue

    for env_var in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
        base = os.environ.get(env_var)
        if base:
            candidates.append(
                str(Path(base) / "Google" / "Chrome" / "Application" / "chrome.exe")
            )

    return candidates


def _macos_candidates() -> list[str]:
    return [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        str(Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    ]


def _linux_candidates() -> list[str]:
    names = (
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "brave-browser",
    )
    return [path for name in names if (path := shutil.which(name))]


def _playwright_chromium() -> str | None:
    """Último recurso: o Chromium que o Playwright já descarregou."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None

    try:
        with sync_playwright() as playwright:
            path = playwright.chromium.executable_path
    except Exception:
        return None

    return path if path and Path(path).exists() else None


def find_chrome(explicit_path: str | None = None) -> str | None:
    """Descobre o executável do Chrome/Chromium no sistema atual."""
    # 1. Argumento explícito
    if explicit_path:
        return explicit_path if Path(explicit_path).exists() else None

    # 2. Variável de ambiente (útil para caminhos fora do padrão)
    env_path = os.getenv("CHROME_PATH")
    if env_path and Path(env_path).exists():
        return env_path

    # 3. Caminhos padrão do sistema operativo
    if os.name == "nt":
        candidates = _windows_candidates()
    elif sys.platform == "darwin":
        candidates = _macos_candidates()
    else:
        candidates = _linux_candidates()

    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return candidate

    # 4. Procura no PATH (cobre instalações atípicas em Linux/macOS)
    for name in ("google-chrome", "chrome", "chromium", "chromium-browser"):
        if found := shutil.which(name):
            return found

    # 5. Chromium do Playwright
    return _playwright_chromium()


def _resolve_profile_dir(profile_dir: Path | str | None = None) -> Path:
    """Resolve o perfil, permitindo override por argumento ou por ambiente."""
    if profile_dir:
        return Path(profile_dir).expanduser().resolve()
    env_profile = os.getenv("CHROME_PROFILE_DIR")
    if env_profile:
        return Path(env_profile).expanduser().resolve()
    return DEFAULT_PROFILE_DIR


def launch_chrome(
    chrome_path: str,
    port: int = DEFAULT_PORT,
    profile_dir: Path | str | None = None,
    url: str | None = None,
) -> subprocess.Popen:
    """Abre o Chrome em modo debug, como processo independente do terminal."""
    profile_dir = _resolve_profile_dir(profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)

    args = [
        chrome_path,
        f"--remote-debugging-port={port}",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-popup-blocking",
    ]
    if url:
        args.append(url)

    kwargs: dict = {
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "stdin": subprocess.DEVNULL,
    }
    if os.name == "nt":
        kwargs["creationflags"] = (
            subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
        )
    else:
        kwargs["start_new_session"] = True

    return subprocess.Popen(args, **kwargs)


def ensure_chrome_debug(
    port: int = DEFAULT_PORT,
    timeout: float = 30.0,
    chrome_path: str | None = None,
    url: str | None = None,
    profile_dir: Path | str | None = None,
) -> bool:
    """Garante que há um Chrome com CDP a escutar na porta.

    Se já estiver a correr, não faz nada. Caso contrário, arranca-o e espera que
    a porta fique disponível. Devolve True em caso de sucesso.
    """
    if port_is_open(port):
        print(f"Chrome debug já está a correr em http://localhost:{port}")
        return True

    chrome = find_chrome(chrome_path)
    if not chrome:
        print(
            "Não encontrei o Google Chrome.\n"
            "Instala o Chrome ou indica o caminho com a variável de ambiente CHROME_PATH "
            "(ou com --chrome-path).",
            file=sys.stderr,
        )
        return False

    print(f"A arrancar Chrome: {chrome}")
    print(f"Perfil: {_resolve_profile_dir(profile_dir)}")
    launch_chrome(chrome, port=port, profile_dir=profile_dir, url=url)

    deadline = time.time() + timeout
    while time.time() < deadline:
        if port_is_open(port):
            print(f"Chrome debug pronto em http://localhost:{port}")
            return True
        time.sleep(0.25)

    print(
        f"O Chrome arrancou mas a porta {port} não respondeu em {timeout:.0f}s.\n"
        "Fecha todas as janelas do Chrome e tenta de novo.",
        file=sys.stderr,
    )
    return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Arranca o Chrome com remote debugging (Windows, macOS, Linux)."
    )
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Porta CDP (padrão: 9222)")
    parser.add_argument("--timeout", type=float, default=30.0, help="Segundos a esperar pelo Chrome")
    parser.add_argument("--chrome-path", default=None, help="Caminho explícito para o executável")
    parser.add_argument("--url", default=None, help="Página a abrir (padrão: página inicial)")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Apenas verifica se o Chrome debug já está a correr",
    )
    args = parser.parse_args(argv)

    if args.check:
        if port_is_open(args.port):
            print(f"Chrome debug está a correr em http://localhost:{args.port}")
            return 0
        print(f"Nada a escutar em http://localhost:{args.port}")
        return 1

    return (
        0
        if ensure_chrome_debug(args.port, args.timeout, args.chrome_path, args.url)
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
