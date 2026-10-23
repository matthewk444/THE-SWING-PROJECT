"""Serve only the live app assets and pose model on loopback."""
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parent
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(ROOT/'live'),**kwargs)
    def do_GET(self):
        if urlsplit(self.path).path=='/model.task':
            model=ROOT/'models'/'pose_landmarker_full.task'
            if not model.exists(): self.send_error(404,'Download pose model first'); return
            self.send_response(200);self.send_header('Content-Type','application/octet-stream');self.send_header('Content-Length',str(model.stat().st_size));self.end_headers()
            with model.open('rb') as f:
                import shutil
                shutil.copyfileobj(f,self.wfile)
            return
        super().do_GET()
    def end_headers(self):
        self.send_header('Permissions-Policy','camera=(self), microphone=()')
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()
    def list_directory(self,path): self.send_error(404); return None
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8502);args=parser.parse_args()
    print(f'Live Swing Lab: http://127.0.0.1:{args.port}',flush=True)
    ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
