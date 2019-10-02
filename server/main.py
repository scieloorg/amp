#!/usr/bin/env python3
"""Article Metadata Predictor"""
from sanic import Sanic

from . import common


app = Sanic(__name__)
app.blueprint(common.bp)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
