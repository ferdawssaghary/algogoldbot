#!/bin/bash

# Script to update the MT5 bridge file timestamp to simulate an active EA
# This keeps the backend from considering the bridge "stale"

BRIDGE_FILE="/workspace/mt5_data/signals.json"

if [ ! -f "$BRIDGE_FILE" ]; then
    echo "Bridge file not found at $BRIDGE_FILE"
    exit 1
fi

echo "Updating bridge file timestamp to keep it fresh..."

# Update the timestamp in the JSON file
current_timestamp=$(date -u +"%Y-%m-%dT%H:%M:%S.%3NZ")
sed -i "s/\"timestamp\": \"[^\"]*\"/\"timestamp\": \"$current_timestamp\"/" "$BRIDGE_FILE"

# Update file modification time
touch "$BRIDGE_FILE"

echo "Bridge file updated with timestamp: $current_timestamp"
echo "File modification time: $(stat -c %y "$BRIDGE_FILE")"