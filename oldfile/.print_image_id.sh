#!/bin/bash

echo ""
echo "Running image ${IMAGE_ID:-UNKNOWN}"
echo ""

echo ""
echo "Software versions from Dockerfile:"
echo "/opt/eudaq2: ${eudaq2_REV_INST}"
echo ""
echo "/opt/corryvreckan: ${corry_REV_INST}"
echo ""

echo""
echo "Current software versions:"
/local/.versions.sh
