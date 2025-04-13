#!/usr/bin/env python3
"""
Script to transform the CSV file to make it compatible with BigQuery.
"""

import os
import csv
import argparse

def transform_csv(input_file, output_file):
    """Transform CSV file to make it compatible with BigQuery."""
    print(f"Transforming {input_file} to {output_file}...")
    
    with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        # Read the header and transform it
        header = next(reader)
        transformed_header = []
        
        # Add a name for the first column if it's empty
        for i, field in enumerate(header):
            if i == 0 and (field == '' or field is None):
                transformed_header.append('row_id')
            else:
                # Replace problematic characters with underscores
                transformed_field = field.replace('.', '_').replace(' ', '_').replace('-', '_').replace('&', 'and')
                transformed_header.append(transformed_field)
        
        # Write the transformed header
        writer.writerow(transformed_header)
        
        # Copy the rest of the data
        for row in reader:
            writer.writerow(row)
    
    print(f"Transformation complete. Output file: {output_file}")
    return True

def main():
    parser = argparse.ArgumentParser(description='Transform CSV file for BigQuery compatibility')
    parser.add_argument('--input-file', required=True, help='Input CSV file')
    parser.add_argument('--output-file', required=True, help='Output CSV file')
    
    args = parser.parse_args()
    
    transform_csv(args.input_file, args.output_file)

if __name__ == "__main__":
    main()
