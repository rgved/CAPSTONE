"""
mock_target_server.py

A standalone, lightweight mock vulnerable web application designed specifically
for demonstrating and testing the Agentic Web Application Security Reconnaissance Platform.

Hosts dedicated endpoints mapped to each OWASP Top 10 (2025) vulnerability category:
- /                             : Central navigation hub linking all test cases
- /login                        : A01 (Missing CSRF) & A07 (Cleartext Auth Transmission)
- /sri-test                     : A08 (External CDN scripts without Subresource Integrity hashes)
- /supply-chain                 : A03 (Outdated client dependencies: jQuery 1.12.4, Bootstrap 3.3.7)
- /error                        : A10 (HTTP 500 error leaking Python framework stack trace)
- /search                       : A05 (Unencoded reflected query parameter injection surface)
- /upload                       : A06 (Insecure design: unconstrained file upload boundary)
- /admin                        : A01 (Unauthenticated administrative management interface)
- /missing-headers              : A02 (Server response completely omitting defensive security headers)
- /actuator/env                 : A02 (Exposed Spring Actuator management environment)

Usage:
    python mock_target_server.py [port]
    (Default port: 8080)
"""
from __future__ import annotations

import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

DEFAULT_PORT = 8080


class MockVulnerableHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A002
        # Clean logging format
        sys.stderr.write(f"[MockTarget] {self.address_string()} - {format % args}\n")

    def do_HEAD(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

    def do_POST(self) -> None:
        # Accept POST submissions and render confirmation
        parsed = urlparse(self.path)
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8", errors="replace")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        response = f"""<!DOCTYPE html>
<html>
<head><title>Action Processed</title></head>
<body>
  <h2>Action Accepted</h2>
  <p>Path: {parsed.path}</p>
  <pre>{body}</pre>
  <p><a href="/">Back to Home</a></p>
</body>
</html>"""
        self.wfile.write(response.encode("utf-8"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)

        # ── Route 1: Index / Navigation Hub ───────────────────────────────────
        if path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Server", "MockTarget/1.0")
            self.end_headers()

            html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vulnerable Benchmark Target - Agentic Security Platform</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; max-width: 900px; margin: 0 auto; line-height: 1.6; }
    h1 { color: #38bdf8; border-bottom: 2px solid #334155; padding-bottom: 0.5rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-top: 1.5rem; }
    .card { background: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 1.25rem; transition: transform 0.15s; }
    .card:hover { transform: translateY(-2px); border-color: #38bdf8; }
    .card h3 { margin: 0 0 0.5rem 0; font-size: 1.1rem; }
    .card a { color: #38bdf8; text-decoration: none; font-weight: bold; }
    .badge { display: inline-block; font-size: 0.7rem; font-weight: bold; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; margin-bottom: 0.5rem; }
    .badge-high { background: #ef444422; color: #ef4444; border: 1px solid #ef444444; }
    .badge-med { background: #f59e0b22; color: #f59e0b; border: 1px solid #f59e0b44; }
    .badge-low { background: #eab30822; color: #eab308; border: 1px solid #eab30844; }
  </style>
</head>
<body>
  <h1>Vulnerable Benchmark Target Application</h1>
  <p>This benchmark application hosts live test fixtures designed for evaluating the <strong>Agentic Security Reconnaissance Platform</strong> against the OWASP Top 10 (2025) vulnerabilities.</p>
  
  <div class="grid">
    <div class="card">
      <span class="badge badge-high">A01 & A07</span>
      <h3><a href="/login">Authentication & Login (/login)</a></h3>
      <p>State-changing login form submitting via POST with <strong>no anti-CSRF token</strong> over cleartext HTTP.</p>
    </div>

    <div class="card">
      <span class="badge badge-low">A08: Integrity</span>
      <h3><a href="/sri-test">Subresource Integrity (/sri-test)</a></h3>
      <p>Third-party CDN scripts loaded <strong>without cryptographic SRI hashes</strong> or crossorigin attributes.</p>
    </div>

    <div class="card">
      <span class="badge badge-med">A03: Supply Chain</span>
      <h3><a href="/supply-chain">Outdated Dependencies (/supply-chain)</a></h3>
      <p>Direct references to legacy libraries with public CVEs (<strong>jQuery 1.12.4</strong>, Bootstrap 3.3.7).</p>
    </div>

    <div class="card">
      <span class="badge badge-med">A10: Exceptional Conditions</span>
      <h3><a href="/error">Server Error & Stack Trace (/error)</a></h3>
      <p>Returns <strong>HTTP 500</strong> with a full Python traceback disclosing runtime paths and database details.</p>
    </div>

    <div class="card">
      <span class="badge badge-med">A05: Injection Surface</span>
      <h3><a href="/search?q=security_test">Reflected Search Vector (/search)</a></h3>
      <p>Search input echoing the <code>?q=</code> parameter directly into the response DOM unencoded.</p>
    </div>

    <div class="card">
      <span class="badge badge-med">A06: Insecure Design</span>
      <h3><a href="/upload">File Ingestion Boundary (/upload)</a></h3>
      <p>Multipart form upload interface with <strong>zero client-side file type</strong> or size constraints.</p>
    </div>

    <div class="card">
      <span class="badge badge-high">A01: Access Control</span>
      <h3><a href="/admin">Administrative Panel (/admin)</a></h3>
      <p>Administrative interface directly reachable without authentication credentials.</p>
    </div>

    <div class="card">
      <span class="badge badge-low">A02: Misconfiguration</span>
      <h3><a href="/missing-headers">Missing Defensive Headers (/missing-headers)</a></h3>
      <p>Response explicitly omitting CSP, Strict-Transport-Security (HSTS), and X-Frame-Options.</p>
    </div>

    <div class="card">
      <span class="badge badge-high">A02: Exposed Endpoint</span>
      <h3><a href="/actuator/env">Spring Actuator (/actuator/env)</a></h3>
      <p>Exposed diagnostic endpoint leaking runtime configuration variables.</p>
    </div>
  </div>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        # ── Route 2: /login (A01 CSRF + A07 Weak Cleartext Auth) ──────────────
        elif path == "/login":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Server", "MockTarget/1.0")
            self.end_headers()

            html = """<!DOCTYPE html>
<html>
<head>
  <title>Login - Customer Portal</title>
  <style>body { font-family: sans-serif; background: #0f172a; color: #fff; padding: 2rem; }</style>
</head>
<body>
  <h2>Customer Account Login</h2>
  <form action="/login" method="POST">
    <div>
      <label>Username / Email:</label><br>
      <input type="text" name="username" placeholder="user@example.com" required>
    </div>
    <br>
    <div>
      <label>Password:</label><br>
      <input type="password" name="password" placeholder="Password" required>
    </div>
    <br>
    <!-- Notice: ZERO CSRF token or nonce input here -->
    <button type="submit">Sign In</button>
  </form>
  <p><a href="/">Back to Home</a></p>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        # ── Route 3: /sri-test (A08 Missing Subresource Integrity) ────────────
        elif path == "/sri-test":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Server", "MockTarget/1.0")
            self.end_headers()

            html = """<!DOCTYPE html>
<html>
<head>
  <title>Third Party Assets Test</title>
  <!-- Missing SRI hashes on external CDN scripts -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</head>
<body>
  <h2>External Third-Party CDN Script Loading</h2>
  <p>This page loads modern scripts from cdnjs and jsdelivr, but omits the <code>integrity="sha384-..."</code> attribute.</p>
  <p><a href="/">Back to Home</a></p>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        # ── Route 4: /supply-chain (A03 Vulnerable Dependencies) ──────────────
        elif path == "/supply-chain":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Server", "MockTarget/1.0")
            self.end_headers()

            html = """<!DOCTYPE html>
<html>
<head>
  <title>Legacy Dependency Portal</title>
  <!-- Legacy jQuery with multiple CVEs (CVE-2015-9251, CVE-2019-11358) -->
  <script src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</head>
<body>
  <h2>Legacy Client Dependencies</h2>
  <p>This page includes legacy jQuery 1.12.4 and Bootstrap 3.3.7 with documented public CVEs.</p>
  <p><a href="/">Back to Home</a></p>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        # ── Route 5: /error (A10 Verbose Error / Stack Trace Disclosure) ───────
        elif path == "/error":
            self.send_response(500)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Server", "MockTarget/1.0")
            self.end_headers()

            html = """<!DOCTYPE html>
<html>
<head><title>500 Internal Server Error</title></head>
<body>
  <h1>HTTP 500: Internal Server Error</h1>
  <p>An unhandled exception occurred during request execution.</p>
  <pre style="background: #111; color: #ff5555; padding: 1rem; border-radius: 4px;">
Traceback (most recent call last):
  File "/srv/web/app/controllers/account_controller.py", line 142, in get_account_summary
    account = db.session.query(Account).filter_by(user_id=target_user_id).one()
  File "/srv/web/venv/lib/python3.11/site-packages/sqlalchemy/orm/query.py", line 2843, in one
    raise NoResultFound("No row was found when one was required")
sqlalchemy.orm.exc.NoResultFound: No row was found when one was required

During handling of the above exception, another exception occurred:
ZeroDivisionError: division by zero
  </pre>
  <p><a href="/">Back to Home</a></p>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        # ── Route 6: /search (A05 Reflected Parameter Surface) ────────────────
        elif path == "/search":
            query_val = qs.get("q", [""])[0] or "sample_query"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Server", "MockTarget/1.0")
            self.end_headers()

            html = f"""<!DOCTYPE html>
<html>
<head><title>Search Catalog</title></head>
<body>
  <h2>Product Catalog Search</h2>
  <form action="/search" method="GET">
    <input type="text" name="q" value="{query_val}" placeholder="Search products...">
    <button type="submit">Search</button>
  </form>
  <div id="results">
    <h3>Search Results for: {query_val}</h3>
    <p>No records matched your search filter for: {query_val}</p>
  </div>
  <p><a href="/">Back to Home</a></p>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        # ── Route 7: /upload (A06 Insecure File Ingestion Boundary) ───────────
        elif path == "/upload":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Server", "MockTarget/1.0")
            self.end_headers()

            html = """<!DOCTYPE html>
<html>
<head><title>User Attachment Ingestion</title></head>
<body>
  <h2>Upload Profile Document</h2>
  <form action="/upload" method="POST" enctype="multipart/form-data">
    <label>Select file to submit:</label><br>
    <!-- Notice: NO accept attribute or type restrictions -->
    <input type="file" name="attachment"><br><br>
    <button type="submit">Upload Attachment</button>
  </form>
  <p><a href="/">Back to Home</a></p>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        # ── Route 8: /admin (A01 Unauthenticated Administrative Surface) ───────
        elif path == "/admin":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Server", "MockTarget/1.0")
            self.end_headers()

            html = """<!DOCTYPE html>
<html>
<head><title>Administrative Control Panel</title></head>
<body>
  <h2>System Management Console</h2>
  <p>Welcome to the Administrative Dashboard (Status: Unrestricted Access).</p>
  <ul>
    <li><a href="/admin/users">User Account Management</a></li>
    <li><a href="/admin/database">Database Backup Tools</a></li>
    <li><a href="/admin/logs">System Audit Logs</a></li>
  </ul>
  <p><a href="/">Back to Home</a></p>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        # ── Route 9: /missing-headers (A02 Missing Defensive Headers) ─────────
        elif path == "/missing-headers":
            self.send_response(200)
            # Only send basic content type; omit all CSP, HSTS, X-Frame-Options
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Server", "Apache/2.4.41")
            self.end_headers()

            html = """<!DOCTYPE html>
<html>
<head><title>Standard Page Without Defensive Headers</title></head>
<body>
  <h2>Standard Web Page</h2>
  <p>This response was sent without Content-Security-Policy, Strict-Transport-Security, or X-Frame-Options.</p>
  <p><a href="/">Back to Home</a></p>
</body>
</html>"""
            self.wfile.write(html.encode("utf-8"))
            return

        # ── Route 10: /actuator/env (A02 Exposed Diagnostics) ─────────────────
        elif path == "/actuator/env":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Server", "MockTarget/1.0")
            self.end_headers()

            json_resp = """{
  "activeProfiles": ["production"],
  "propertySources": [
    {
      "name": "systemEnvironment",
      "properties": {
        "DATABASE_URL": {"value": "postgres://admin:secret@db.internal:5432/prod"},
        "JWT_SECRET": {"value": "super-secret-key-12345"}
      }
    }
  ]
}"""
            self.wfile.write(json_resp.encode("utf-8"))
            return

        # ── 404 Fallback ──────────────────────────────────────────────────────
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>404 Not Found</h1><p><a href='/'>Return to Home</a></p>")


def run_server(port: int = DEFAULT_PORT) -> None:
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, MockVulnerableHandler)
    print("=" * 65)
    print(f"  Mock Vulnerable Target Server running at http://127.0.0.1:{port}/")
    print("  Endpoints ready for automated security reconnaissance:")
    print(f"    - http://127.0.0.1:{port}/login             (CSRF & Weak Cleartext Auth)")
    print(f"    - http://127.0.0.1:{port}/sri-test          (Missing SRI hashes)")
    print(f"    - http://127.0.0.1:{port}/supply-chain      (Outdated jQuery/Bootstrap)")
    print(f"    - http://127.0.0.1:{port}/error             (HTTP 500 Stack Trace)")
    print(f"    - http://127.0.0.1:{port}/search?q=test     (Reflected Query Parameter)")
    print(f"    - http://127.0.0.1:{port}/upload            (Unconstrained File Upload)")
    print(f"    - http://127.0.0.1:{port}/admin             (Exposed Admin Surface)")
    print(f"    - http://127.0.0.1:{port}/missing-headers   (Missing Defensive Headers)")
    print("=" * 65)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        httpd.server_close()


if __name__ == "__main__":
    port = DEFAULT_PORT
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    run_server(port)
