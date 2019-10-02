#!/usr/bin/env python3
"""Article Metadata Predictor"""
from sanic import Sanic

from . import common, w2v1


app = Sanic(__name__)
app.blueprint(common.bp)
app.blueprint(w2v1.bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
