#!/bin/bash


# Check if an output file is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 output_file.csv"
    exit 1
fi

output_file=$1

rm "$output_file"
# Create output file with header if it doesn't exist
if [ ! -f "$output_file" ]; then
    echo "new_rnti,existing_rnti" > "$output_file"
fi

# Function to process each line
process_line() {
    line=$1
    echo "$line" # Output the line to standard output

    # Use grep to find the pattern and awk to extract the numbers
    echo "$line" | grep -o "User 0x[0-9a-fA-F]* requesting RRC Reestablishment as 0x[0-9a-fA-F]*" | awk '{print $2","$7}' >> "$output_file"
}

# Read lines from stdin
while IFS= read -r line
do
    process_line "$line"
done