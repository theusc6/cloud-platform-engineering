# Event Emitter Script

The Event Emitter Script is designed to emit custom events to a specific AWS EventBridge event bus. It provides a way to generate and send events with custom data to an EventBridge event bus.

## Prerequisites

- Python 3.x installed on your system.
- AWS CLI configured with valid credentials and a named profile.

## Installation

1. Clone this repository to your local machine:

   ```bash
   git clone https://github.com/theusc6/cloud-platform-engineering.git
   ```

2. Move into the project directory and install the dependencies

    ``` bash
    cd cloud-platform-engineering
    ```

3. Install the required Python packages using pip:

   ```bash
   pip install -r cpe_project/requirements.txt
   ```

## Usage

Run the script with the following command:

```bash
python emit_event.py -p <AWS_PROFILE_NAME>
```

Replace `<AWS_PROFILE_NAME>` with the name of your AWS CLI profile, which is required for SSO login.

## How It Works

The script uses the AWS SDK for Python (Boto3) to emit an event to a specified EventBridge event bus. It constructs an event payload in JSON format and sends it to the event bus using the `put_events` method.

The script accepts a single argument:

 `-p` or `--profile`: The AWS profile name to use for SSO login.

### Event Payload

The script emits a custom event with the following payload format:

```json
{
    "id": "111",
    "when": "2023-07-12T15:00:00Z",
    "correlation_id": "111",
    "payload": {
        "report_number": "111",
        "redacted_id": "111"
    }
}
```

The event includes attributes like `id`, `when`, `correlation_id`, and `payload`. You can customize the payload data as needed.

## Output

The script will output the response from the event emission, indicating whether the event was successfully emitted or if an error occurred.

## Notes

Please ensure you review and understand any script before running it to ensure it aligns with your specific requirements and intended outcome.
