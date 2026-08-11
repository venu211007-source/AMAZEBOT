#!/bin/bash

echo ""
echo " =========================================="
echo "    AMAZEBOT - A Teenager Innovation"
echo "    Tribute to Suman Dutta sir"
echo " =========================================="
echo ""
echo "  Project Members:"
echo "  G Venugopalan, Mahalakshmi R,"
echo "  Ram Eswar, Sleva Vignesh"
echo " =========================================="
echo ""

# Try Python 3
if command -v python3 &>/dev/null; then
    echo " Starting server with Python3..."
    echo " Open this in your browser:"
    echo " http://localhost:8080/static/index.html"
    echo ""
    echo " Press Ctrl+C to stop."
    echo ""
    # Auto-open browser
    if command -v open &>/dev/null; then
        sleep 1 && open "http://localhost:8080/static/index.html" &
    elif command -v xdg-open &>/dev/null; then
        sleep 1 && xdg-open "http://localhost:8080/static/index.html" &
    fi
    python3 -m http.server 8080
    exit 0
fi

# Try Python 2
if command -v python &>/dev/null; then
    echo " Starting server with Python..."
    echo " Open: http://localhost:8080/static/index.html"
    echo ""
    sleep 1 && open "http://localhost:8080/static/index.html" 2>/dev/null &
    python -m SimpleHTTPServer 8080
    exit 0
fi

# Try Node.js
if command -v npx &>/dev/null; then
    echo " Starting server with Node.js..."
    echo " Open: http://localhost:3000"
    echo ""
    sleep 1 && open "http://localhost:3000" 2>/dev/null &
    npx serve static -p 3000
    exit 0
fi

echo " ERROR: Python or Node.js not found!"
echo ""
echo " Install Python from: https://www.python.org/downloads/"
echo " Or Node.js from: https://nodejs.org/"
echo ""
