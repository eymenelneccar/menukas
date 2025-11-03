import os
import json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import base64
import re
import time
import io


ROOT_DIR = os.path.abspath(os.getcwd())
ASSETS_MENU_PATH = os.path.join(ROOT_DIR, 'assets', 'menu.json')
ASSETS_CATEGORIES_PATH = os.path.join(ROOT_DIR, 'assets', 'categories.json')
ASSETS_SETTINGS_PATH = os.path.join(ROOT_DIR, 'assets', 'settings.json')
ASSETS_ANNOUNCEMENTS_PATH = os.path.join(ROOT_DIR, 'assets', 'announcements.json')
ASSETS_HERO_PATH = os.path.join(ROOT_DIR, 'assets', 'hero.json')


class Handler(SimpleHTTPRequestHandler):
    # تأكد من تقديم الملفات من مجلد المشروع
    def __init__(self, *args, **kwargs):
        kwargs['directory'] = ROOT_DIR
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/api/menu':
            try:
                with open(ASSETS_MENU_PATH, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        elif self.path == '/api/categories':
            try:
                with open(ASSETS_CATEGORIES_PATH, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        elif self.path == '/api/settings':
            try:
                with open(ASSETS_SETTINGS_PATH, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        elif self.path == '/api/announcements':
            try:
                with open(ASSETS_ANNOUNCEMENTS_PATH, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        elif self.path == '/api/hero':
            try:
                with open(ASSETS_HERO_PATH, 'r', encoding='utf-8') as f:
                    data = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(data.encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        else:
            # ملفات ثابتة
            return super().do_GET()

    def do_POST(self):
        if self.path == '/api/save-menu':
            length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode('utf-8'))
                if not isinstance(data, list):
                    raise ValueError('Payload must be a JSON array')
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
                return

            # اكتب إلى ملف الأصول
            try:
                os.makedirs(os.path.dirname(ASSETS_MENU_PATH), exist_ok=True)
                with open(ASSETS_MENU_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'path': 'assets/menu.json'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        elif self.path == '/api/upload-image':
            ctype = self.headers.get('Content-Type', '')
            if 'multipart/form-data' in ctype:
                # تحليل multipart بدون cgi (متوافق مع Python 3.13+)
                m = re.search(r'boundary=(?:"?)([^";]+)', ctype)
                if not m:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': False, 'error': 'Missing boundary'}).encode('utf-8'))
                    return
                boundary = m.group(1).encode('utf-8')
                length = int(self.headers.get('Content-Length', '0'))
                body = self.rfile.read(length)

                def parse_multipart(body_bytes, boundary_bytes):
                    delimiter = b'--' + boundary_bytes
                    parts_raw = body_bytes.split(delimiter)
                    parts = []
                    for part in parts_raw:
                        if not part or part.strip() in (b'', b'--'):
                            continue
                        part = part.lstrip(b'\r\n')
                        # قص النهاية
                        if part.endswith(b'\r\n'):
                            part = part[:-2]
                        if part.endswith(b'--'):
                            part = part[:-2]
                        header_end = part.find(b'\r\r\n')
                        if header_end == -1:
                            header_end = part.find(b'\r\n\r\n')
                        if header_end == -1:
                            continue
                        headers_raw = part[:header_end].decode('iso-8859-1')
                        content = part[header_end+4:]
                        headers = {}
                        for line in headers_raw.split('\r\n'):
                            if ':' in line:
                                k, v = line.split(':', 1)
                                headers[k.strip().lower()] = v.strip()
                        cd = headers.get('content-disposition', '')
                        name_m = re.search(r'name="([^"]+)"', cd)
                        filename_m = re.search(r'filename="([^"]+)"', cd)
                        name = name_m.group(1) if name_m else None
                        filename = filename_m.group(1) if filename_m else None
                        parts.append({'name': name, 'filename': filename, 'content': content, 'headers': headers})
                    return parts

                parts = parse_multipart(body, boundary)
                file_part = None
                for p in parts:
                    if p.get('name') in ('image', 'file'):
                        file_part = p
                        break
                if not file_part and parts:
                    file_part = parts[0]
                if not file_part or not file_part.get('content'):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': False, 'error': 'No file uploaded'}).encode('utf-8'))
                    return

                filename = file_part.get('filename') or f"img_{int(time.time()*1000)}.bin"
                safe_name = re.sub(r'[^A-Za-z0-9._-]+', '_', filename)
                img_dir = os.path.join(ROOT_DIR, 'assets', 'images')
                os.makedirs(img_dir, exist_ok=True)
                abs_path = os.path.join(img_dir, safe_name)
                with open(abs_path, 'wb') as f:
                    f.write(file_part['content'])
                rel_path = os.path.join('assets', 'images', safe_name).replace('\\', '/')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'path': rel_path}).encode('utf-8'))
            else:
                # معالجة رفع بصيغة JSON مع dataURL/base64
                length = int(self.headers.get('Content-Length', '0'))
                body = self.rfile.read(length)
                try:
                    payload = json.loads(body.decode('utf-8'))
                    data_url_or_b64 = payload.get('data')
                    filename = payload.get('filename')
                    if not data_url_or_b64:
                        raise ValueError('Missing image data')

                    m = re.match(r'^data:(image/[\w.+-]+);base64,(.*)$', data_url_or_b64)
                    if m:
                        mime = m.group(1)
                        b64data = m.group(2)
                    else:
                        mime = None
                        b64data = data_url_or_b64

                    ext_map = {'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp', 'image/svg+xml': '.svg'}
                    ext = ext_map.get(mime, '')
                    if not filename:
                        filename = f"img_{int(time.time()*1000)}{ext or '.bin'}"

                    safe_name = re.sub(r'[^A-Za-z0-9._-]+', '_', filename)
                    img_dir = os.path.join(ROOT_DIR, 'assets', 'images')
                    os.makedirs(img_dir, exist_ok=True)
                    abs_path = os.path.join(img_dir, safe_name)

                    with open(abs_path, 'wb') as f:
                        f.write(base64.b64decode(b64data))

                    rel_path = os.path.join('assets', 'images', safe_name).replace('\\', '/')
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': True, 'path': rel_path}).encode('utf-8'))
                except Exception as e:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        elif self.path == '/api/save-categories':
            length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode('utf-8'))
                if not isinstance(data, list):
                    raise ValueError('Payload must be a JSON array')
                os.makedirs(os.path.dirname(ASSETS_CATEGORIES_PATH), exist_ok=True)
                with open(ASSETS_CATEGORIES_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'path': 'assets/categories.json'}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        elif self.path == '/api/save-settings':
            length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode('utf-8'))
                if not isinstance(data, dict):
                    raise ValueError('Payload must be a JSON object')
                os.makedirs(os.path.dirname(ASSETS_SETTINGS_PATH), exist_ok=True)
                with open(ASSETS_SETTINGS_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'path': 'assets/settings.json'}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        elif self.path == '/api/save-announcements':
            length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode('utf-8'))
                if not isinstance(data, dict):
                    raise ValueError('Payload must be a JSON object')
                os.makedirs(os.path.dirname(ASSETS_ANNOUNCEMENTS_PATH), exist_ok=True)
                with open(ASSETS_ANNOUNCEMENTS_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'path': 'assets/announcements.json'}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        elif self.path == '/api/save-hero':
            length = int(self.headers.get('Content-Length', '0'))
            body = self.rfile.read(length)
            try:
                data = json.loads(body.decode('utf-8'))
                if not isinstance(data, dict):
                    raise ValueError('Payload must be a JSON object')
                os.makedirs(os.path.dirname(ASSETS_HERO_PATH), exist_ok=True)
                with open(ASSETS_HERO_PATH, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': True, 'path': 'assets/hero.json'}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({'ok': False, 'error': str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({'ok': False, 'error': 'Not Found'}).encode('utf-8'))


def main():
    port = int(os.environ.get('PORT', '8000'))
    httpd = ThreadingHTTPServer(('', port), Handler)
    print(f"Serving at http://localhost:{port}/ (root: {ROOT_DIR})")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == '__main__':
    main()