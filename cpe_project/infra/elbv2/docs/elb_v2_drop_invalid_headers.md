# Overview
This script will ensure that Elastic Load Balancers (ELB) will drop invalid HTTP headers. 
By default, Application Load Balancers are not configured to drop invalid HTTP header values. Removing these header values prevents HTTP desync attacks.

## Action
The script modifies the value of routing.http.drop_invalid_header_fields.enabled is set to true.

## Usage
The script can be ran by the following:

```
python elb_v2_drop_invalid_headers.py --profile <insert profile> --region <insert region> --load_balancer <insert lb id>
```

## Target
Run this script in any account where an ELBv2 fails compliance checks. 

## Considerations
Always validate that changes made to production resources have been validated and approved by resource owner and via an official change process.
