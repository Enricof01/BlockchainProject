import threading
from flask import Flask, jsonify


class Node:

    def __init__(self, node_name, port):
        self.node_name = node_name
        self.port = port

        # 1. Flask-Instanz in der Klasse erstellen
        self.app = Flask(node_name)

        # 2. Die Routen (Endpoints) für diese Node definieren
        self.setup_routes()

    def setup_routes(self):
        # Wichtig: Weil wir in einer Klasse sind, nutzen wir self.app.route
        @self.app.route("/info", methods=["GET"])
        def get_info():
            return jsonify(
                {
                    "node": self.node_name,
                    "status": "online",
                    "mempool_size": 0,  # Hier kämen später deine echten Daten hin
                }
            )

    def run(self, debug=False, use_threading=False):
        print(f" Starte {self.node_name} auf Port {self.port}...")

        # Option A: Blockierend (Standard)
        if not use_threading:
            self.app.run(host="0.0.0.0", port=self.port, debug=debug)

        # Option B: Im Hintergrund (perfekt, wenn du mehrere Nodes in EINEM Skript testen willst)
        else:
            thread = threading.Thread(
                target=self.app.run,
                kwargs={"host": "0.0.0.0", "port": self.port, "debug": debug},
            )
            thread.daemon = True
            thread.start()

def test():
    enrico = Node(node_name="hallo", port=3000)
    enrico.run()
    print("running")

if __name__ == "__main__":
    test()