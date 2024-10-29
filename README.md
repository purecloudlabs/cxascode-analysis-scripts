# Introduction
As the support team for CX as Code we are sometimes pulled in to look at a customer's environment or one of our own internal environment and understand what is going on in their Terraform/CX as Code environment.

As a result of these requests we have a written a number of python and and juypter notebook scripts to process ana analyze the data.  We are release these into our lab environment "AS-IS" with no guarantee of support.  Our goals to share these scripts so that the large CX as Code community can use them as they see fit.

# Installation

All requirements were captured in a Python `requirements.txt` file.  The libaries can be
installed using `pip install -r requirements.txt"

# Configuration
All paths used in these notebooks read from commonlib/config.Config class.  This class will read and write based on three environment variables:

```
export TERRAFORM_LOG_PATH=""  #Location of the log file
export NORMALIZED_TERRAFORM_LOG_PATH="" #Output path fo the normalized Terraform log data
export NORMALIZED_GENESYS_SDK_PATH=""   #Output path ot the normalized SDK data
```

# Additional notes
The `notebooks` directory contains two files: `plan-analysis.ipynb` and `sdk-notebook.ipynb` file.  

The `plan-analysis.ipynb` file is a Juypter notebook that will take the STDOUT from the running of `terraform plan` or `tofu` plan and parse the results to identify long plan resolution times, drift detection, etc...

The `sdk-notebook.ipynb' will parse the output from a STDOUT run of a `TF_DEBUG=json terraform apply --auto-approve` and will break down the API calls being made in the plan. 

The `notebooks/common-lib` contains python functions used to carry out various functions in processing.

The `generator` folder is a small python script used to generate a large number of resources.  This was so we could use it to create enough to parse and log the output.