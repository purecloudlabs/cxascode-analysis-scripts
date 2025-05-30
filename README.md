# Introduction
As the support team for CX as Code, we are sometimes pulled in to examine a customer's environment or one of our own internal environments to understand what is happening in their Terraform/CX as Code environment.

As a result of these requests, we have written several Python and Jupyter Notebook scripts to process and analyze the data.  We are releasing these into our lab environment "AS-IS" with no guarantee of support.  Our goal is to share these scripts so that the large CX as Code community can use them as they see fit.

# Installation

All requirements were captured in a Python `requirements.txt` file.  The libraries can be
installed using `pip install -r requirements.txt`.

# Configuration
All paths used in these notebooks are read from commonlib/config.Config class.  This class will read and write based on three environment variables:

```
export TERRAFORM_LOG_PATH=""  #Location of the log file
export NORMALIZED_TERRAFORM_LOG_PATH="" #Output path fo the normalized Terraform log data
export NORMALIZED_GENESYS_SDK_PATH=""   #Output path ot the normalized SDK data
```

# Additional notes
The `sdk-plan-notebooks` directory contains two files: `plan-analysis.ipynb` and `sdk-notebook.ipynb`.  

The `plan-analysis.ipynb` file is a Jupyter notebook that will take the STDOUT from the running of `terraform plan` or `tofu` plan and parse the results to identify long plan resolution times, drift detection, etc...

The `sdk-notebook.ipynb' will parse the output from a STDOUT run of a `TF_DEBUG=json terraform apply --auto-approve` and will break down the API calls being made in the plan. 

The `notebooks/common-lib` contains Python functions used to carry out various functions in processing.

The `generator` folder is a small Python script used to generate a large number of resources.  This was so we could use it to create enough to parse and log the output.
