# Import required libraries for subprocess execution, timing, system operations and JSON handling
import subprocess, time, sys, json

# Default version placeholder used in provider.tf
placeholder_version = '0.0.0'
# File to store timing data results
plan_data_file = 'data.json'

# List of Terraform provider versions to test
versions = [
    placeholder_version,
    '1.30.2',
    '1.31.0',
    '1.32.0',
    '1.32.1',
    '1.33.0',
    '1.34.0',
    '1.35.0',
    '1.36.0',
    '1.36.1',
    '1.37.0',
    '1.38.0',
    '1.38.1',
    '1.39.0',
    '1.40.0',
    '1.40.1',
    '1.41.0',
    '1.42.0',
    '1.43.0',
    '1.43.1',
    '1.44.0',
    '1.44.1',
    '1.45.0',
    '1.46.0',
    '1.47.0',
    '1.48.0',
    '1.48.1',
    '1.48.2',
    '1.48.3',
    '1.49.0',
    '1.49.1',
    ]

# Class to store details about each Terraform plan execution
class PlanDetails:
    def __init__(self, version, duration):
        self.version = version
        self.duration = duration
    
    # Convert plan details to dictionary format for JSON serialization
    def to_dict(self):
        return {
            'version': self.version,
            'duration': self.duration
        }
    
# Write collected timing data to JSON file
def write_data_to_file(data):
    with open(plan_data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Main function to test different Terraform versions
def test_versions(command):
    data = []
    last_version = versions[len(versions) - 1]
    # Iterate through versions, testing each one
    for i, prev in enumerate(versions):
        if i == len(versions) -1:
            break
        current_index = i + 1
        current_version = versions[current_index]
        replace_version(prev, current_version)
        
        print('sleeping...')
        time.sleep(1)

        run_terraform_init_upgrade()

        # Time the execution of terraform command
        start = time.time()
        run_terraform_command(version=current_version, command=command)
        end = time.time()

        duration = end - start 

        # Store results
        plan = PlanDetails(current_version, duration)
        data.append(plan.to_dict())
    
    write_data_to_file(data)
    replace_version(last_version, placeholder_version)

# Run terraform init with upgrade flag
def run_terraform_init_upgrade():
    command = 'terraform init -upgrade'
    subprocess.run(command, shell=True)

# Execute terraform command and capture output
def run_terraform_command(version, command):
    v = version.replace('.', '_')
    output_file_name = f'./plans/{v}.json'
    
    with open(output_file_name, 'w') as file:
        process = subprocess.run(command,  stdout=file, stderr=file)

    if process.returncode == 0:
        print('finished successful plan')
    else:
        print(f'error occurred: {process.stderr.decode()}')
        sys.exit()

# Update provider version in provider.tf file
def replace_version(prev, new):
    print(f'replacing {prev} with {new}')

    file_name = 'provider.tf'
    with open(file_name, 'r') as file:
        filedata = file.read()
    filedata = filedata.replace(prev, new)
    with open(file_name, 'w') as file:
        file.write(filedata)

# Generate Terraform configuration file with 296 queue resources and data sources
def write_queues_file():
    with open('queues.tf', 'w') as txt_file:
        for x in range(296):
            txt_file.write(f'\nresource "genesyscloud_routing_queue" "queue{x}" {{ name = "a queue {x}" }} \n')
            txt_file.write(f'\ndata "genesyscloud_routing_queue" "queue{x}" {{ name = genesyscloud_routing_queue.queue{x}.name }} \n')

# Test a single version of Terraform
def test_current_version(id, command):
    start = time.time()
    run_terraform_command(id, command)
    end = time.time()
    print(f'\nFinished in {end - start} for {id}\n')

# Main execution block
if __name__ == '__main__':
    # Generate queue configuration file
    write_queues_file()
  
    # Define terraform commands
    apply_command = ['terraform', 'apply', '--auto-approve']
    plan_command = ['export TF_LOG=json','terraform', 'plan']
    # Run tests with apply command
    test_versions(command=apply_command)
    #test_current_version(id='we_will_see_plan', command=apply_command)
    
