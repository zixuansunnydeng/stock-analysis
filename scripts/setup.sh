#!/bin/bash
# Setup script for the Stock Market dbt Project

# Create directories if they don't exist
mkdir -p data
mkdir -p ~/.dbt

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "Terraform is not installed. Please install Terraform first."
    exit 1
fi

# Check if dbt is installed
if ! command -v dbt &> /dev/null; then
    echo "dbt is not installed. Would you like to install it now? (y/n)"
    read -r install_dbt
    if [[ $install_dbt == "y" ]]; then
        pip install dbt-bigquery
    else
        echo "Please install dbt manually before continuing."
        exit 1
    fi
fi

# Check if required Python packages are installed
echo "Checking required Python packages..."
pip install kaggle google-cloud-storage google-cloud-bigquery

# Copy example files
echo "Creating configuration files from examples..."
if [ ! -f terraform/terraform.tfvars ]; then
    cp terraform/terraform.tfvars.example terraform/terraform.tfvars
    echo "Created terraform/terraform.tfvars - please edit with your GCP details"
fi

if [ ! -f ~/.dbt/profiles.yml ]; then
    cp dbt_project/profiles.yml.example ~/.dbt/profiles.yml
    echo "Created ~/.dbt/profiles.yml - please edit with your GCP details"
fi

# Prompt for Kaggle credentials
echo "Do you want to set up Kaggle credentials now? (y/n)"
read -r setup_kaggle
if [[ $setup_kaggle == "y" ]]; then
    echo "Enter your Kaggle username:"
    read -r kaggle_username
    echo "Enter your Kaggle API key:"
    read -r kaggle_key
    
    # Set environment variables
    export KAGGLE_USERNAME=$kaggle_username
    export KAGGLE_KEY=$kaggle_key
    
    # Create .kaggle directory and config file
    mkdir -p ~/.kaggle
    echo "{\"username\":\"$kaggle_username\",\"key\":\"$kaggle_key\"}" > ~/.kaggle/kaggle.json
    chmod 600 ~/.kaggle/kaggle.json
    
    echo "Kaggle credentials set up successfully"
else
    echo "Please set up Kaggle credentials manually before downloading the dataset"
fi

echo "Setup complete! Next steps:"
echo "1. Edit terraform/terraform.tfvars with your GCP project details"
echo "2. Run 'cd terraform && terraform init && terraform apply'"
echo "3. Edit ~/.dbt/profiles.yml with your GCP connection details"
echo "4. Run the data download script: python scripts/download_and_load_data.py"
echo "5. Run dbt: cd dbt_project && dbt run"
