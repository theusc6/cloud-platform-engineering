# AWS Config Query Script

This script allows you to run AWS Config queries for an AWS account. AWS Config is a service that enables you to assess, audit, and evaluate the configurations of your AWS resources. The script provides the results in either YAML or JSON format.

## How to Use

1. Ensure you have Python installed on your system.
2. Install the required dependencies by running `pip install boto3 pyyaml argparse`.
3. Save the script in a file named `aws_config_query.py`.
4. Make sure you have configured AWS CLI credentials or set up the appropriate environment variables for AWS access.
5. Open a terminal or command prompt, navigate to the directory where the script is located, and execute it with the following command:

```bash
python aws_config_query.py <aws_profile> <query_file> [-aggregator <aggregator>] [-output <output_format>]
```

Replace the placeholders:

- `<aws_profile>`: The name of the AWS profile that will be used for authentication. This profile should be defined in your AWS credentials file or environment.
- `<query_file>`: The path to a file containing the AWS Config query you want to execute. The query should be written in AWS Config Query Language.
- `<aggregator>` (optional): If your query needs to be executed on an aggregator, you can specify the aggregator name using this option.
- `<output_format>` (optional): You can choose to get the results in either YAML (default) or JSON format by specifying `yaml` or `json`.

## Script Execution

The script follows the following steps:

1. Parses the command-line arguments provided by the user using the `argparse` library.
2. Sets up an AWS session using the provided AWS profile, assuming the necessary credentials have been properly configured.
3. Initializes an AWS Config client using the `boto3` library.
4. Reads the AWS Config query from the specified query file.
5. Executes the query using the AWS Config client. If an aggregator is specified, it runs the query using `select_aggregate_resource_config`. Otherwise, it runs the query using `select_resource_config`.
6. Prints the query results. The results are extracted from the response and displayed in either YAML or JSON format, based on the user's choice.

If any errors occur during the execution, the script will print an error message with a brief description of the issue.

## Example Usage

1. Run a basic AWS Config query using the default AWS profile:

    ```bash
    python aws_config_query.py default_profile config_query.txt
    ```

2. Run a query using a specific aggregator and get the results in JSON format:

    ```bash
    python aws_config_query.py my_profile query.txt -aggregator my_aggregator -output json
    ```

Please ensure you have the necessary permissions and configurations set up for AWS Config queries to execute successfully.
