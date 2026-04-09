import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CREDENTIALS_PATH = Path.home() / '.config' / 'higgsfield' / 'credentials.json'


def get_token() -> str:
    if not CREDENTIALS_PATH.exists():
        print('Not authenticated. Run: python3 login.py', file=sys.stderr)
        sys.exit(1)

    try:
        with open(CREDENTIALS_PATH) as f:
            credentials = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f'Invalid credentials file: {e}', file=sys.stderr)
        print('Run: python3 login.py', file=sys.stderr)
        sys.exit(1)

    token = credentials.get('access_token')
    if not token:
        print('No access_token in credentials. Run: python3 login.py', file=sys.stderr)
        sys.exit(1)

    expires_at = credentials.get('expires_at')
    if expires_at:
        try:
            if datetime.now(timezone.utc) >= datetime.fromisoformat(expires_at):
                print('Session expired. Run: python3 login.py', file=sys.stderr)
                sys.exit(1)
        except ValueError:
            pass

    return token


if __name__ == '__main__':
    print(get_token())
