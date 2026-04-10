
# SecurityHub Lambda Functions

## All things Lambda for SecurityHub

### Some thoughts on approach

#### Example

`lambda-export-secuty-hub-findings`

This Lambda function exports Security Hub findings to an XLSX file in memory and then uploads it to an S3 bucket.

---

This AWS Lambda function does **NOT** take any command-line arguments. Instead, it takes an `event` and a `context` parameter. The `event` parameter is used to pass data to the function, while the `context` parameter provides information about the runtime environment.

In this case, the `event` parameter is not being used, it's inclusion is for compatibility with the Lambda function interface.

Also **note** that the function doesn't filter by severity level, it exports *ALL* findings.

---

This Lambda function should be scheduled to run on the first day of every month, which is done by a `CloudWatch Events` rule with a `cron` expression that triggers the function at the desired time. Alternatively, you can set up an API Gateway trigger to allow the function to be run on-demand.

---

### Setup the **Cloudwatch Events** rule

1. Go to the AWS Management Console and navigate to the CloudWatch service.

2. In the left sidebar, click on "Events" under the "Events" section.

3. `Click` the "Create rule" button.

4. In the "Define pattern" section, select the "Schedule" radio button.

5. In the "Schedule expression" field, enter the following cron expression:

```bash
cron(0 0 1 * ? *)

The above cron expression triggers the function at midnight (0 0) on the first day of every month (1 *).
```

6. Click on "Add target".

7. Choose the "Lambda function" option.

8. Select your Lambda function from the "Function" dropdown.

9. Click "Configure details".

10. Give your rule a name and description.

    1. Optionally, you can add tags to the rule.

11. Click "Create rule".
