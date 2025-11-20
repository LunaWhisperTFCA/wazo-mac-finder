# Wazo MAC Finder

A simple, robust, and cross-platform Python script to find a device in a Wazo instance by its MAC address.

This script is designed to be straightforward to set up and use. It correctly uses `X-Auth-Token` for authentication and reliably loads configuration from a `.env` file located in the same directory.

## Setup

1.  **Install Dependencies:**
    Make sure you have Python 3 installed. Then, install the required packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment:**
    Create a `.env` file by copying the example template:
    ```bash
    cp .env.example .env
    ```
    Now, edit the `.env` file and add your Wazo server URL and your long-lived authentication token:
    ```ini
    WAZO_HOST=https://your-wazo-ip-or-domain.com
    WAZO_TOKEN=your-long-lived-auth-token
    ```

## Usage

Run the script from your terminal, providing the MAC address you want to search for with the `-m` or `--mac` flag.

```bash
python3 main.py -m 00:1A:2B:3C:4D:5E
```

### Options

*   `--mac <address>`: (Required) The MAC address to find.
*   `--host <url>`: Override the `WAZO_HOST` from the `.env` file.
*   `--token <token>`: Override the `WAZO_TOKEN` from the `.env` file.
*   `--insecure`: Use this flag if your Wazo server has a self-signed SSL certificate.
*   `--output <format>`: Choose the output format. Can be `json` (default), `text`, or `csv`.
*   `-v, --verbose`: Enable detailed logging for debugging.

### Example with insecure flag

```bash
python3 main.py -m 00:1A:2B:3C:4D:5E --insecure
```
