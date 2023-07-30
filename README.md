# Reddit Account Creator
Python program that creates reddit accounts with verified emails (optional) using [selenium 4.8.3](https://pypi.org/project/selenium/4.8.3) and [openai-whisper 20230314](https://pypi.org/project/openai-whisper/20230314/). The emails used by this program are taken from https://internxt.com/temporary-email.
**This is for educational purposes only and should not be used to mass create bot accounts or such.**

[Python 3.8+](https://www.python.org/downloads/) is required.

## Setup
1. Install the requirements in `requirements.txt`.
    ```
    pip install -r requirements.txt
    ```

1. Run the script.
    ```
    python src/main.py
    ```

1. (If you create multiple accounts) Switch your ip after running the script using a vpn or such. Reddit has a limit of one account per 10 minutes. If you don't change ips the program will close itself.

## Customization
You are able to customize how the account is being created. Just change some things in the `config.json` file and run the program again. Below you can see the description of each setting:

| Setting | Description |
|---------|-------------|
| `webdriver` | Choose between `firefox` and `chrome` as your webdriver. |
| `verify_email_address` | Wether or not the email should be verified or not. |
| `authentic_input` | If the script should use authentic input (enabling may help with reCAPTCHA). |
| `create_authentic_account` | Wether or not the account should join random subreddits and customize its avatar. |
| `audio_language` | As this script solves the reCAPTCHA using the audio challenge it's required to set a language. |

You are also able to change the way the username is being generated. As of now, the program will just use usernames recommended by reddit. Inside `customization.py` you can find the `generate_account_username` function which handles the generation of usernames (as the name suggests). So just change up the code to generate unique names. **NOTE: THE PROGRAM DOES NOT CHECK IF A USERNAME IS AVAILABLE OR NOT SO YOU HAVE TO CHECK YOURSELF**