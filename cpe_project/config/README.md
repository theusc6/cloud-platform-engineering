# AWS Config Query Tool

This simple python script will run a AWS Config query. This can be run directly against an account, or you can use an aggregator in an account to query all AWS resoruces. The query must be kept in a text file and passed in as an argument to the script. The following example queries are included in this directory:

- compliantCount.txt : List the number of compliant and non-compliant assets
- countEC2.txt : List the number of types of EC2 machines
- countEC2byAccountid.txt : List the number of EC2 instances per account
- runningEC2.txt : Report on EC2 instance details that are running

For a list of example Config queries, go to https://docs.aws.amazon.com/config/latest/developerguide/example-query.html

## Usage
python .\queryConfig.py --help                                                                                     
```usage: queryConfig.py [-h] [-aggregator AGGREGATOR] [-output OUTPUT] aws_profile query_file

Run AWS Config query for an AWS account

positional arguments:
  aws_profile           AWS profile
  query_file            File containing the query

options:
  -h, --help            show this help message and exit
  -aggregator AGGREGATOR
                        Use the specified Aggregator
  -output OUTPUT        [defult yaml] or json
  ```

  ## Example Output


> % python queryConfig.py -aggregator aws-controltower-GuardrailsComplianceAggregator audit .\countEC2.txt
```
Query Results:
COUNT(*): 10
configuration:
  instanceType: c4.4xlarge

COUNT(*): 2
configuration:
  instanceType: c5.2xlarge

COUNT(*): 4
configuration:
  instanceType: c5.large

COUNT(*): 1
configuration:
  instanceType: c5.xlarge

COUNT(*): 3
configuration:
  instanceType: g5.2xlarge

COUNT(*): 6
configuration:
  instanceType: m5.2xlarge

COUNT(*): 3
configuration:
  instanceType: m5.xlarge

COUNT(*): 1
configuration:
  instanceType: m5a.xlarge

COUNT(*): 1
configuration:
  instanceType: m6a.xlarge

COUNT(*): 9
configuration:
  instanceType: t2.large

COUNT(*): 3
configuration:
  instanceType: t2.medium

COUNT(*): 48
configuration:
  instanceType: t2.micro

COUNT(*): 1
configuration:
  instanceType: t2.small

COUNT(*): 13
configuration:
  instanceType: t3.2xlarge

COUNT(*): 4
configuration:
  instanceType: t3.large

COUNT(*): 4
configuration:
  instanceType: t3.medium

COUNT(*): 5
configuration:
  instanceType: t3.micro

COUNT(*): 4
configuration:
  instanceType: t3.small

COUNT(*): 1
configuration:
  instanceType: t3.xlarge
  ```


> % python queryConfig.py -o json -aggregator aws-controltower-GuardrailsComplianceAggregator audit .\countEC2byAccountid.txt 
```
Query Results:
{
  "COUNT(*)": 2,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 2,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 5,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 60,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 2,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 2,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 1,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 2,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 1,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 15,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 2,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 4,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 3,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 1,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 1,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 2,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 1,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 3,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 2,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 1,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 7,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 2,
  "accountId": "123456789012"
}
{
  "COUNT(*)": 2,
  "accountId": "123456789012"
}
```

