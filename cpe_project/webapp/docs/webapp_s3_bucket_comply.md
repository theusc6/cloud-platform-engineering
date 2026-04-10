# S3 Security Settings Enforcer

This script is designed to enforce various security settings for Amazon S3 buckets based on the guidelines provided in the AWS Security Hub documentation. It covers the following security controls:

- [S3.1] S3 Block Public Access setting should be enabled
- [S3.4] S3 buckets should have server-side encryption enabled
- [S3.9] S3 bucket server access logging should be enabled
- [S3.14] S3 buckets should use versioning

## Prerequisites

- Python 3.x
- AWS CLI configured with necessary credentials and a profile

## Installation

1. Clone the repository to your local machine:

   ```sh
   git clone https://github.com/theusc6/cloud-platform-engineering.git
   ```

2. Navigate to the repository directory:

   ```sh
   cd cloud-platform-engineering/cpe_project/webapp
   ```

## Usage

1. Run the script using the following command:

   ```sh
   python webapp_s3_bucket_comply.py
   ```

2. Access the script through your web browser at `http://localhost:5000/`.

3. Enter the AWS profile name and the name of the S3 bucket you want to enforce security settings for.

4. Click the "Enforce Security Settings" button.

## Web Interface

The script provides a simple web interface to interact with. It allows you to input the AWS profile name and S3 bucket name. Upon clicking the "Enforce Security Settings" button, the script enforces the specified security settings on the S3 bucket.

## Notes

- The script uses the Flask framework for the web interface.
- The specified S3 bucket must exist in your AWS account.
- The script interacts with AWS S3 using the provided AWS profile credentials.

## Contributors

- [Your Name](https://github.com/your-username)

## License

This project is licensed under the [MIT License](LICENSE).