#!/bin/bash

input_dir="$1"
output_dir="$input_dir/resized"
mkdir -p "$output_dir"

for img in "$input_dir"/*.bmp; do
    filename=$(basename "$img")
    width=$(sips -g pixelWidth "$img" | awk '/pixelWidth/ {print $2}')
    new_width=$((width / 2))
    sips --resampleWidth $new_width "$img" --out "$output_dir/$filename"
done
