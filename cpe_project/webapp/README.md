
# Python Webapps

This code defines two routes: `/` for the main page and `/webapp_s3_bucket_comply.py` to handle the form submission.

When the user submits the form, the `webapp_s3_bucket_comply` function is called, which performs the S3 compliance checks and returns the results to the user.

```bash
.
├── README.md
├── images
│   ├── no_bucket.png
│   ├── output.png
│   ├── output_page.png
│   └── start_page.png
├── requirements.txt
├── templates
│   ├── index.html
│   └── results.html
└── webapp_s3_bucket_comply.py

3 directories, 9 files
```

The index function simply returns a template for the main page, which contains a form that allows the user to enter the bucket name and AWS profile name.

The `webapp_s3_bucket_comply` function gets the form data, sets up the boto3 client, performs the compliance checks, and returns the results to the user using a result template.

Note that you will need to create two templates

1. `index.html` for the main page.
2. `result.html` for the results page.

These templates are stored in the `templates` directory within your project.

To run the web app, make sure you install any dependencies, e.g. Flask `pip install flask`, and run the app with `python webapp_s3_bucket_comply.py`.

You can also follow this general guide

Clone the repository

```bash
git clone https://github.com/theusc6/myorg-devsecops.git
```

Move into the project directory

```bash
cd myorg-devsecops/src/python/webapp
```

Install the requirements

```bash
pip install -r requirements.txt
```

Start the local server

```bash
NY-IT-MAC-01:webapp user$ python webapp_s3_bucket_comply.py 
 * Serving Flask app 'webapp_s3_bucket_comply'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 531-671-779
127.0.0.1 - - [05/May/2023 13:45:01] "POST / HTTP/1.1" 200 -
```

The app will be available at [http://localhost:5000](http://localhost:5000).

## Start Page

Enter your bucket name and the corresponding `AWS config profile` name into the appropriate text boxes below:

![S3 Bucket Enforcer](images/start_page.png)

Click on __Enforce compliance__

## Output Example

![S3 Bucket Enforcer](images/output_page.png)

if the bucket name does not exist

![S3 Bucket Enforcer](images/no_bucket.png)

### THE END
