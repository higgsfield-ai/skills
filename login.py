import json
import os
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

DEVICE_AUTH_URL = os.getenv(
    'HIGGSFIELD_DEVICE_AUTH_URL',
    'https://fnf-device-auth.higgsfield.ai',
)
CREDENTIALS_PATH = Path.home() / '.config' / 'higgsfield' / 'credentials.json'
KEEP_POLLING_ERRORS = {'authorization_pending', 'slow_down'}


def _parse_response(raw: str) -> Dict[str, Any]:
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return {'detail': raw or 'empty response'}


def _post(path: str, body: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], int]:
    url = DEVICE_AUTH_URL + path
    data = json.dumps(body).encode() if body else b''
    request = Request(
        url,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'higgsfield-cli/1.0',
        },
        method='POST',
    )

    try:
        with urlopen(request, timeout=30) as response:
            return _parse_response(response.read().decode()), response.status
    except HTTPError as error:
        return _parse_response(error.read().decode()), error.code
    except (URLError, OSError) as error:
        return {'detail': str(error)}, 0


def _save_credentials(access_token: str, expires_in: int) -> None:
    expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)

    credentials = {
        'access_token': access_token,
        'expires_at': expires_at.isoformat(),
    }

    with open(CREDENTIALS_PATH, 'w') as f:
        json.dump(credentials, f, indent=2)


def main() -> None:
    data, status = _post('/authorize')

    if status != 200:
        print('Failed to request device code: ' + str(data), file=sys.stderr)
        sys.exit(1)

    verification_uri = data['verification_uri']
    device_code = data['device_code']
    interval = data['interval']
    expires_in = data['expires_in']

    print('Opening browser for authentication...')
    print(f'If browser does not open, visit: {verification_uri}')
    webbrowser.open(str(verification_uri))
    print('Waiting for approval...')

    deadline = time.monotonic() + expires_in

    while time.monotonic() < deadline:
        time.sleep(interval)

        data, status = _post('/token', {'device_code': device_code})

        if status == 200:
            _save_credentials(data['access_token'], data['expires_in'])
            print('Successfully authenticated!')
            return

        detail = data.get('detail', '')

        if detail == 'slow_down':
            interval += 5

        if detail not in KEEP_POLLING_ERRORS:
            print('Authorization failed: ' + detail, file=sys.stderr)
            sys.exit(1)

    print('Device code expired. Please try again.', file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
    main()
