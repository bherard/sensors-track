# Raspberry related software.

## How to test
0. `cd src`
1. `python -m venv venv`
2. `. ./venv/bin/activate`
3. `export PYTHONPATH=$(pwd)`
4. `bin/webapp`
5. Web API documentation is then available at http://localhost:8080/doc

**NOTE:**

In this mode config file is in [./src/sensotrack/conf/sensotrack.json](./src/sensotrack/conf/sensotrack.json).

If file `/etc/sensotrack/sensotrack.json` exists it's used instead.
