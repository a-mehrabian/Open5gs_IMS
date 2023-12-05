#!/bin/bash


if [ "$#" -ne 1 ]; then
    echo "Usage: $0 output_file.csv"
    exit 1
fi

output_file=$1

rm "$output_file"

if [ ! -f "$output_file" ]; then
    echo "new_rnti,existing_rnti" > "$output_file"
fi

process_line() {
    line=$1
    echo "$line"

    echo "$line" | grep -o "User 0x[0-9a-fA-F]* requesting RRC Reestablishment as 0x[0-9a-fA-F]*" | awk '{print $2","$7}' >> "$output_file"
}

while IFS= read -r line
do
    process_line "$line"
done