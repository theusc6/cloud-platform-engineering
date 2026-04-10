# S3 VPC Flow Logs Query Script

This is a Python script that queries an Amazon S3 bucket containing VPC flow logs to find log files that match a specific port number and IP address within a defined time range. The script uses the AWS SDK for Python (Boto3) to interact with the S3 service and perform the query.

## Usage

Before running the script, ensure you have the necessary AWS credentials set up. The script uses the provided AWS profile name to authenticate with AWS.

### Script Parameters

The script takes the following command-line arguments:

1. `--bucket`: (required) Name of the S3 bucket that contains the VPC flow logs.
2. `--folder`: (required) Folder path within the bucket where the log files are stored.
3. `--profile`: (required) The AWS profile name to be used for authentication.
4. `--port`: (required) The port number to search for in the VPC flow logs.
5. `--ip`: (required) The IP address to search for in the VPC flow logs.
6. `--time-range`: (optional) Time range in hours to search for logs. Default is 3 hours.

### Script Logic

1. The script imports necessary modules, including `argparse` for command-line argument parsing, `gzip` for decompressing log files, `datetime` for handling timestamps, and `boto3` for interacting with the AWS S3 service.

2. The `search_logs_in_s3` function is defined, which performs the log query based on the provided parameters.

3. The script checks if it is being run as the main module (`__name__ == '__main__'`) and proceeds to parse the command-line arguments.

4. The function `search_logs_in_s3` is called with the parsed arguments, triggering the log search process.

5. Within the `search_logs_in_s3` function, a Boto3 session is created with the provided AWS profile, and an S3 client is instantiated.

6. The script calculates the start time of the time range based on the current time and the specified time range in hours.

7. It lists all objects in the specified folder path within the S3 bucket using the `list_objects_v2` method.

8. For each log object found, the script checks if it falls within the specified time range.

9. If the log object is within the time range, it retrieves the log content from the S3 object and decompresses it if necessary.

10. The log content is then converted to a string, and the script searches for the desired patterns: the specified port number (`--port`) and IP address (`--ip`).

11. If the patterns are found in the log content, the log file's S3 URL and the log content are printed to the console.

12. The script continues the search process for all log files within the specified time range.

## Example Usage

```bash
python3 s3_log_query.py \
    --bucket my-vpc-flow-logs \
    --folder logs \
    --profile my_aws_profile \
    --port 80 \
    --ip 203.0.113.10 \
    --time-range 6
```

This command queries the S3 bucket "my-vpc-flow-logs" within the "logs" folder using the AWS profile "my_aws_profile" to search for VPC flow logs containing the port number 80 and the IP address 203.0.113.10 within the last 6 hours.

Please ensure you have the necessary AWS credentials and permissions to access the specified S3 bucket and its contents before running the script.
