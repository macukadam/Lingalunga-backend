#!/bin/bash

url="http://localhost:8000/api/s3/all-files/"
number_of_requests=11

for i in $(seq 1 $number_of_requests); do
  echo "Sending request $i..."
  curl -s -X GET "$url" & # The & symbol sends the request in the background
done

wait # Wait for all background processes to finish
echo "All requests completed."
