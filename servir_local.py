"""Sirve esta carpeta en http://localhost:8000 para probar CEOExplorer en local.

Cada página HTML se entrega con la cabecera Clear-Site-Data, que le pide al navegador borrar la caché, el
almacenamiento y los service workers que hubieran quedado de otro proyecto en el mismo puerto (por eso a veces
localhost:8000 mostraba otra app). También desactiva la caché, para ver siempre la última versión.

Uso: python servir_local.py          (o python servir_local.py 8081 para otro puerto)
"""
import http.server
import sys


class Manejador(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        if self.path.split("?")[0].endswith((".html", "/")):
            self.send_header("Clear-Site-Data", '"cache", "storage"')
        super().end_headers()


if __name__ == "__main__":
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"CEOExplorer en http://localhost:{puerto}/index.html  (Ctrl+C para detener)")
    http.server.ThreadingHTTPServer(("", puerto), Manejador).serve_forever()
