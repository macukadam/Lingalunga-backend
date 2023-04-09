#!/bin/bash

while getopts r: flag
do
    case "${flag}" in
        r) repeat=${OPTARG};;
    esac
done

url="http://127.0.0.1/api/openai/create-story/"
number_of_requests=$repeat

time(
    for i in $(seq 1 $number_of_requests); do
      # echo "Sending request $i..."
      curl -s -X GET "$url"

      wait # Wait for all background jobs to finish
    done

)

echo "All requests completed."
