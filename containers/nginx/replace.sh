#!/bin/sh

from_what=$1
to_what=$2
where=$3

if grep -q "$from_what" "$where"; then
    # Replace the old line with the new line
    sed -i "s/$from_what/$to_what/" "$where"
    echo "Replaced '$from_what' with '$to_what' in $where."
else
    echo "Line '$from_what' not found in $where."
fi

# Test Nginx configuration for syntax errors
nginx -t

# Reload Nginx to apply the changes
if [ $? -eq 0 ]; then
    echo "Reloading Nginx..."
    systemctl reload nginx
    echo "Nginx reloaded successfully."
else
    echo "Nginx configuration test failed. Please check the configuration."
fi
