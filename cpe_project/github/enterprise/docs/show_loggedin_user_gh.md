# GitHub Enterprise User Information Script

This script uses the GitHub CLI tool (`gh`) to retrieve and display user information from a GitHub account. The script executes the `gh api /user` command to fetch the authenticated user's details from the GitHub API. It then parses and displays relevant user information in the terminal.

## Script Functionality

1. The script initiates a subprocess to execute the `gh api /user` command, which retrieves user information using the GitHub API.

2. The script checks if the subprocess execution was successful (return code 0) or not.

   - If successful, the JSON response received from the command's standard output is parsed.
   - If unsuccessful, an error message is displayed along with any available error output from the subprocess.

3. If the subprocess was successful, the script extracts and prints the following user information:

   - Username
   - Full Name
   - Email
   - Bio
   - Number of Followers
   - Number of Following
   - Number of Public Repositories
   - Company
   - Location
   - Account Creation Date

## How to Use

1. Make sure you have the GitHub CLI tool (`gh`) installed on your system.

2. Save the script into a file (e.g., `show_loggedin_user_gh.py`).

3. Open a terminal and navigate to the directory containing the script.

4. Run the script using the command: `python show_loggedin_user_gh.py`

5. The script will authenticate using your GitHub credentials (if not authenticated already) and retrieve your user information. The retrieved information will be displayed in the terminal.

Please note that if you encounter any issues, such as authentication errors or interruptions, appropriate error messages will be displayed to guide you.

This script can be useful to quickly retrieve and display basic user information directly from the command line using the GitHub CLI tool.
