"""Restore the bundled cooking video. No downloads or third-party packages."""
from pathlib import Path
import hashlib
import json
ROOT = Path(__file__).resolve().parent

def prepare_media():
    source = ROOT / 'media' / 'cooking'
    target = ROOT / 'dist' / 'assets' / 'cooking.mp4'
    manifest = json.loads((source / 'manifest.json').read_text())
    if target.is_file() and target.stat().st_size == manifest['size']:
        if hashlib.sha256(target.read_bytes()).hexdigest() == manifest['sha256']:
            return
    temporary = target.with_suffix('.mp4.tmp')
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        with temporary.open('wb') as output:
            for part in manifest['parts']:
                data = (source / part['file']).read_bytes()
                if len(data) != part['size'] or hashlib.sha256(data).hexdigest() != part['sha256']:
                    raise ValueError('Video part is damaged: ' + part['file'])
                output.write(data)
        if hashlib.sha256(temporary.read_bytes()).hexdigest() != manifest['sha256']:
            raise ValueError('Video verification failed. Download the complete repository again.')
        temporary.replace(target)
        print('Bundled video is ready.', flush=True)
    finally:
        if temporary.exists():
            temporary.unlink()

if __name__ == '__main__':
    prepare_media()
