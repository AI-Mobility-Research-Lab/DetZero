#!/usr/bin/env python
"""Lightweight training monitor with optional email alerts.

Usage:
  python train_monitor.py --log /path/to/log --pid <train_pid> [--interval 30]

Email (optional) via SMTP env or flags:
  TRAIN_MONITOR_SMTP_HOST, TRAIN_MONITOR_SMTP_PORT,
  TRAIN_MONITOR_SMTP_USER, TRAIN_MONITOR_SMTP_PASS,
  TRAIN_MONITOR_EMAIL_FROM, TRAIN_MONITOR_EMAIL_TO
"""
import argparse
import os
import smtplib
import time
from email.message import EmailMessage
from typing import List, Optional, Tuple


def parse_args():
    parser = argparse.ArgumentParser(description="Monitor a training log and optionally send email on finish/fail.")
    parser.add_argument("--log", required=True, help="Path to the training log file to monitor.")
    parser.add_argument("--pid", type=int, default=None, help="PID of the training process (for liveness checks).")
    parser.add_argument("--interval", type=float, default=30.0, help="Polling interval in seconds.")
    parser.add_argument("--max-tail", type=int, default=50, help="Number of log lines to include in the report.")
    parser.add_argument("--smtp-host", default=os.environ.get("TRAIN_MONITOR_SMTP_HOST"), help="SMTP host.")
    parser.add_argument("--smtp-port", type=int, default=int(os.environ.get("TRAIN_MONITOR_SMTP_PORT", 587)), help="SMTP port.")
    parser.add_argument("--smtp-user", default=os.environ.get("TRAIN_MONITOR_SMTP_USER"), help="SMTP username.")
    parser.add_argument("--smtp-pass", default=os.environ.get("TRAIN_MONITOR_SMTP_PASS"), help="SMTP password.")
    parser.add_argument("--email-to", default=os.environ.get("TRAIN_MONITOR_EMAIL_TO"), help="Notification recipient.")
    parser.add_argument("--email-from", default=os.environ.get("TRAIN_MONITOR_EMAIL_FROM"), help="Notification sender.")
    return parser.parse_args()


def process_alive(pid: Optional[int]) -> Optional[bool]:
    """Check whether a PID is alive. Returns None if pid not provided."""
    if pid is None:
        return None
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def tail_lines(path: str, n: int) -> List[str]:
    """Return last n lines from a file without loading the whole thing."""
    try:
        with open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            block = bytearray()
            step = 1024
            while size > 0 and block.count(b"\n") <= n:
                take = min(step, size)
                size -= take
                f.seek(size)
                block[:0] = f.read(take)
            return block.decode(errors="ignore").splitlines()[-n:]
    except FileNotFoundError:
        return []


def classify_state(lines: List[str]) -> Optional[Tuple[str, str]]:
    """Return (state, note) if a terminal state is detected."""
    joined = "\n".join(lines)
    if "End training" in joined or "**********************End training" in joined:
        return ("success", "Found 'End training' marker in log.")
    if "Traceback" in joined or "RuntimeError" in joined or "CUDA error" in joined:
        return ("failed", "Found error markers in log.")
    return None


def send_email(subject: str, body: str, args) -> None:
    """Send an email if SMTP and addresses are configured; otherwise noop with a note."""
    if not (args.email_to and args.email_from and args.smtp_host and args.smtp_user and args.smtp_pass):
        print("[monitor] Email not sent: SMTP/addresses not fully configured.")
        return
    msg = EmailMessage()
    msg["From"] = args.email_from
    msg["To"] = args.email_to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(args.smtp_host, args.smtp_port) as server:
        server.starttls()
        server.login(args.smtp_user, args.smtp_pass)
        server.send_message(msg)
    print("[monitor] Email sent to", args.email_to)


def main():
    args = parse_args()
    if not os.path.isfile(args.log):
        raise FileNotFoundError(f"Log file not found: {args.log}")

    print(f"[monitor] Watching {args.log} every {args.interval:.1f}s (pid={args.pid or 'n/a'})")
    while True:
        time.sleep(args.interval)
        lines = tail_lines(args.log, max(args.max_tail, 10))
        state = classify_state(lines)
        alive = process_alive(args.pid)

        if state:
            final_state, note = state
            summary_lines = lines[-args.max_tail :]
            subject = f"[DetZero] Train {final_state}"
            body = f"{note}\n\nLast {len(summary_lines)} log lines:\n" + "\n".join(summary_lines) + "\n"
            print(f"[monitor] Detected terminal state: {final_state} ({note})")
            send_email(subject, body, args)
            break

        if alive is False:
            summary_lines = lines[-args.max_tail :]
            subject = "[DetZero] Train stopped"
            body = (
                f"Training process pid={args.pid} is no longer running and no success marker was found.\n\n"
                f"Last {len(summary_lines)} log lines:\n" + "\n".join(summary_lines) + "\n"
            )
            print("[monitor] Process ended without success marker.")
            send_email(subject, body, args)
            break

        # keep-alive heartbeat to stdout
        progress_line = lines[-1] if lines else "(no log lines yet)"
        print(f"[monitor] alive={alive} progress: {progress_line}")


if __name__ == "__main__":
    main()
