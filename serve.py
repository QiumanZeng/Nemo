"""Local-only static preview, with byte ranges for video seeking."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import re
import argparse
import webbrowser
ROOT=Path(__file__).resolve().parent/'dist'
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs): super().__init__(*args,directory=str(ROOT),**kwargs)
 def send_head(self):
  path=Path(self.translate_path(self.path))
  r=self.headers.get('Range')
  self.remaining=None
  if not r or not path.is_file():return super().send_head()
  size=path.stat().st_size;m=re.fullmatch(r'bytes=(\d*)-(\d*)',r)
  if not m or not any(m.groups()):self.send_error(416);return None
  a,b=m.groups();start=int(a) if a else max(0,size-int(b));end=min(int(b),size-1) if a and b else size-1
  if start>end or start>=size:
   self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return None
  f=path.open('rb');f.seek(start);self.remaining=end-start+1
  self.send_response(206);self.send_header('Content-Type',self.guess_type(str(path)))
  self.send_header('Accept-Ranges','bytes');self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.send_header('Content-Length',str(self.remaining));self.end_headers();return f
 def copyfile(self,source,outputfile):
  try:
   if self.remaining is None:return super().copyfile(source,outputfile)
   while self.remaining:
    block=source.read(min(1024*1024,self.remaining))
    if not block:break
    outputfile.write(block);self.remaining-=len(block)
  except (BrokenPipeError,ConnectionResetError):pass
if __name__=='__main__':
 from prepare_media import prepare_media
 prepare_media()
 parser=argparse.ArgumentParser(description='Run Nemo locally; no Python packages required.')
 parser.add_argument('--port',type=int,default=8767)
 parser.add_argument('--open',action='store_true',help='Open Nemo in the default browser')
 args=parser.parse_args()
 if not 1 <= args.port <= 65535:parser.error('port must be between 1 and 65535')
 if not (ROOT/'index.html').is_file():parser.error('dist/index.html is missing. Please extract the complete repository.')
 try:server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
 except OSError as exc:
  parser.exit(1,f'Cannot start local server: {exc}\nTry another port: python3 serve.py --port 8768\n')
 url=f'http://127.0.0.1:{args.port}/'
 print(f'Nemo: {url}\nKeep this terminal open. Press Ctrl+C to stop.',flush=True)
 if args.open:webbrowser.open(url)
 try:server.serve_forever()
 except KeyboardInterrupt:print('\nNemo stopped.')
 finally:server.server_close()
