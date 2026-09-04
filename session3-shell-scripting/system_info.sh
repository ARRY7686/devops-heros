
#!/bin/bash

# Store system information in variables
current_date=$(date)
hostname=$(hostname)
username=$(whoami)
disk_usage=$(df -h)

# Print current date
echo "Current Date: $current_date"

# Print hostname
echo "Hostname: $hostname"

# Print username
echo "Username: $username"

# Print disk usage
echo "Disk Usage:"
echo "$disk_usage"

# Take input from user
read -p "Enter the name of the directory to create: " directory

# Create directory
mkdir -p "$directory"

# Create a file inside the directory
touch "$directory/processes.txt"

# Store running processes in the file using output redirection
ps > "$directory/processes.txt"

echo "Running processes have been saved to $directory/processes.txt"

# Print running processes
echo "Running Processes:"
ps
