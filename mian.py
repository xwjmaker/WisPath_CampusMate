import subprocess
import sys
import os
import signal
import atexit

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "mianyang-campus", "backend")
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "mianyang-campus", "frontend")

processes = []


def cleanup():
    for p in processes:
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()


atexit.register(cleanup)
for sig in (signal.SIGINT, signal.SIGTERM):
    try:
        signal.signal(sig, lambda *_: cleanup())
    except AttributeError:
        pass


def main():
    print("=" * 50)
    print("  智慧校园AI服务平台 - 启动中...")
    print("=" * 50)
    print(f"  后端: http://localhost:8000")
    print(f"  前端: http://localhost:5173")
    print(f"  按 Ctrl+C 停止所有服务")
    print("=" * 50)

    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        cwd=BACKEND_DIR,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    processes.append(backend)

    npm = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=FRONTEND_DIR,
        shell=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    processes.append(npm)

    try:
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        cleanup()


if __name__ == "__main__":
    main()
