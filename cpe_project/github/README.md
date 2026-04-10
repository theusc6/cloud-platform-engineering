
# Python for GitHub

## Some scripts that may be useful for GitHub automation

### Example

#### login for programmatic access

```bash
aws sso login --profile myorg-training
```

#### Check options/requirements for this script, or any other script in this repo

```bash
python ~/github.com/theusc6/myorg-devsecops/devops/github/python/export_org_archive_to_s3.py -h
usage: export_org_archive_to_s3.py [-h] -p PROFILE

Create an Organization Archive for theusc6 from GitHub.com and export to AWS S3.

options:
  -h, --help            show this help message and exit
  -p PROFILE, --profile PROFILE
                        AWS profile name for SSO login
```

#### run the GitHub archive to S3 script

```bash
python ~/github.com/theusc6/myorg-devsecops/devops/github/python/export_org_archive_to_s3.py -p myorg-training
```

#### Output

``` bash
Downloading: 238B [00:00, 832B/s] 
Downloading: 7.00B [00:00, 163B/s]
.
.
.
Failed to download https://api.github.com/repos/theusc6/SparkleTransporter/zipball: 400 Client Error: Bad Request for url: https://codeload.github.com/theusc6/SparkleTransporter/legacy.zip/?token=AXXBGBXH3BDNWIA2M5IQH73EHWTLM
.
.
.
File SparkleTransporter.zip not found
File SparkleASCTransporter.zip not found
File inscription-ocr.zip not found
File InfoSec-Metrics-API.zip not found
File AWSInternalVPC.zip not found
File edgevpc.zip not found
File aws_stitch_vpc.zip not found
File beacon-sanbox.zip not found
File beacon-ports-adapters-shell.zip not found
File Sparkle_RD.zip not found
File sparkle-rnd-DistributedPipeline.zip not found
File sparkle-rnd-inclusions_tracking_to_3D.zip not found
File sparkle-rnd-rendering-client.zip not found
File sparkle-rnd-inclusion_videos.zip not found
File sparkle-rnd-Template_Fit_APIs.zip not found
File sparkle-rnd-template_predict_and_fit.zip not found
File sparkle-rnd-SparkleImageProcessing.zip not found
File sparkle-rnd-SparkleMiddleware.zip not found
File sparkle-rnd-SparkleAutoPlot.zip not found
File sparkle-rnd-SparkleInference.zip not found

Total repos in org: 176
Total repos in archive: 176

Uploading theusc6_archive_20230417_161724.zip to S3 myorg-github-archives bucket...
Upload Successful: theusc6_archive_20230417_161724.zip
Removing local file...
```

#### Confirm the new archive is in S3

![S3-confirmation](images/S3-confirmation.png)

# Testing

## this took a long time but is making progress

```bash
NY-IT-MAC-01:python user$ pwd
/home/user/myorg-devsecops/python/devops/github/python

NY-IT-MAC-01:python user$ coverage run --source=. -m unittest discover tests
Downloading: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 1.00/1.00 [00:00<00:00, 23.3kB/s]
.Upload Successful: s3_file_name
.
----------------------------------------------------------------------
Ran 2 tests in 0.013s

OK

NY-IT-MAC-01:python user$ coverage report
Name                                     Stmts   Miss  Cover
------------------------------------------------------------
create_new_repo.py                          25     25     0%
export_org_archive_to_rubrik.py             74     74     0%
export_org_archive_to_s3.py                 94     64    32%
github_listr.py                             28     28     0%
github_listr_fmt.py                         19     19     0%
org_user_list.py                            43     43     0%
org_user_profile.py                         64     64     0%
org_user_with_no_repos.py                   32     32     0%
public_list.py                              29     29     0%
tests/test_export_org_archive_to_s3.py      38      1    97%
------------------------------------------------------------
TOTAL                                      446    379    15%

NY-IT-MAC-01:python user$ coverage xml
Wrote XML report to coverage.xml
```

### What it looks like in here

```bash
NY-IT-MAC-01:python user$ tree ../
../
├── README.md
└── python
    ├── README.md
    ├── __pycache__
    │   └── export_org_archive_to_s3.cpython-311.pyc
    ├── coverage.xml
    ├── create_new_repo.py
    ├── export_org_archive_to_rubrik.py
    ├── export_org_archive_to_s3.py
    ├── github_listr.py
    ├── github_listr_fmt.py
    ├── images
    │   └── S3-confirmation.png
    ├── org_user_list.py
    ├── org_user_profile.py
    ├── org_user_with_no_repos.py
    ├── public_list.py
    ├── repo.tar.gz
    ├── requirements.txt
    └── tests
        ├── __pycache__
        │   └── test_export_org_archive_to_s3.cpython-311.pyc
        └── test_export_org_archive_to_s3.py

6 directories, 18 files
```
