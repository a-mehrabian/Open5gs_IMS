#!/bin/bash


if [ "$#" -ne 2 ]; then
    echo "Usage: $0 input_file output_file"
    exit 1
fi

input_file=$1
output_file=$2

rm "$output_file"

if [ ! -f "$output_file" ]; then
    echo "tmsi,imsi" > "$output_file"
fi

while true; do
    if [ -f "$input_file" ]; then
        break
    else
        echo "Waiting for input file ($input_file) to be created..."
        sleep 2
    fi
done

tail -f "$input_file" | while IFS= read -r line; do
    if echo "$line" | awk '/M_TMSI:/ && /IMSI\[/ && !/IMSI\[Unknown\]/' >/dev/null; then
        tmsi=$(echo "$line" | grep -o 'M_TMSI:[^]]*' | awk -F':' '{print $2}')
        imsi=$(echo "$line" | grep -o 'IMSI[^]]*' | awk -F'[' '{print $2}' | tr -d ']')
        if [[ -n "$tmsi" && -n "$imsi" && "$tmsi" != " " && "$imsi" != " " ]]; then
            echo "$tmsi,$imsi" >> "$output_file"
        fi
    fi
done
