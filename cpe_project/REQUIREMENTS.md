# How to use PIP

Use the `pipreqs` tool to generate a `requirements.txt` file containing the packages used in your project directory. `pipreqs` scans your project's Python files and identifies the imported packages, then generates a list of those packages along with their versions.

Here's how you can use `pipreqs`:

1. **Install `pipreqs`:**

You can install `pipreqs` using `pip`:

```bash
pip install pipreqs
```

2. **Generate `requirements.txt`:**

Navigate to your project directory in the terminal and run `pipreqs` to generate the `requirements.txt` file:

```bash
pipreqs .
```

This will scan the current directory and its subdirectories for Python files and generate a `requirements.txt` file with the required packages.

3. **View the Generated `requirements.txt`:**

You can now view the contents of the generated `requirements.txt` file:

```bash
cat requirements.txt
```

This file will contain the list of packages used in your project, along with their versions.

Keep in mind that `pipreqs` generates a list of packages based on the imported modules in your Python files. It doesn't differentiate between packages used in your application code and packages used for development or testing purposes. Therefore, it's a good practice to manually review and edit the `requirements.txt` file to remove any unnecessary or development-specific packages.

Using `pipreqs` can be a convenient way to generate a `requirements.txt` file tailored to your project's dependencies.

---
---

You can also use `pipreqs` to generate a list of requirements without actually creating a new `requirements.txt` file. Additionally, you can compare the generated requirements with an existing `requirements.txt` file to identify differences. Here's how you can achieve both:

1. **Generate a List of Requirements without Creating a File:**

You can use the `--print` flag with `pipreqs` to print the list of requirements to the terminal without creating a new `requirements.txt` file. Navigate to your project directory in the terminal and run the following command:

```bash
pipreqs --print .
```

This will print the list of required packages along with their versions directly to the terminal.

2. **Compare with an Existing `requirements.txt` File:**

If you have an existing `requirements.txt` file and you want to compare the generated requirements with it, you can use the `diff` command in the terminal. First, generate the requirements using `pipreqs` as mentioned earlier:

```bash
pipreqs --print .
```

Then, compare the generated requirements with your existing `requirements.txt` file:

```bash
pipreqs --print . | diff - requirements.txt
```

This command will display the differences between the two sets of requirements, indicating which packages are present in one list but not the other.

Using these methods, you can generate a list of requirements with `pipreqs` without creating a new file and compare it to an existing `requirements.txt` file to identify any differences in package requirements.
