import requests
import json
import base64
import re
from urllib.parse import unquote

# Function to check if a string is base64
def is_base64(s: str) -> bool:
    try:
        if len(s) % 4 == 0:
            # Decode and re-encode to check if the string is valid base64
            decoded = base64.urlsafe_b64decode(s + '==')  # Add padding for valid base64
            return base64.urlsafe_b64encode(decoded).decode('utf-8').rstrip('=') == s
        return False
    except Exception:
        return False

# Function to decode the base64 URL
def decode_base64_url(base64_url: str) -> str:
    base64_url = base64_url.rstrip("=")
    padding = '=' * ((4 - len(base64_url) % 4) % 4)
    base64_url += padding  # Ensure proper base64 padding
    decoded_bytes = base64.urlsafe_b64decode(base64_url)
    return decoded_bytes.decode("utf-8")

# Function to handle LootLink URL and bypass its redirection
def lootlink_bypass(lootlink_url: str) -> str:
    try:
        # Check if the LootLink URL contains the base64 encoded part
        match = re.search(r"r=([^&]+)", lootlink_url)
        if match:
            base64_part = match.group(1)
            
            # Check if it's a valid base64 string
            if is_base64(base64_part):
                # Decode the base64 URL part
                decoded_url = decode_base64_url(base64_part)

                # Optionally, you can extract more details from the decoded URL
                # Here we assume it will be a redirect link or API token
                return decoded_url
            else:
                return "Invalid LootLink base64 data."
        else:
            return "LootLink URL format not valid."
    except Exception as e:
        return f"An error occurred during LootLink bypass: {str(e)}"

# Function to get the delta key using HWID
def get_delta_key(hwid: str):
    # Check if the HWID starts with the Platoboost URL and remove it if present
    if hwid.startswith('https://gateway.platoboost.com/a/8?id='):
        hwid = hwid.replace('https://gateway.platoboost.com/a/8?id=', '')

    code = "DNHA"  # Code to be used in the authentication

    # Prepare the payload for the request
    payload = {
        "captcha": "",
        "type": "Turnstile"
    }

    session = requests.Session()

    # Perform POST and PUT requests to authenticate and retrieve the key
    session.post(f"https://api-gateway.platoboost.com/v1/sessions/auth/8/{hwid}", json=payload)
    session.put(f"https://api-gateway.platoboost.com/v1/sessions/auth/8/{hwid}/{code}")
    
    # Adding a small delay to ensure the requests are properly handled
    session.put(f"https://api-gateway.platoboost.com/v1/sessions/auth/8/{hwid}/{code}")

    # Get the response containing the redirect URL with the encoded token
    response = session.get(f"https://api-gateway.platoboost.com/v1/authenticators/8/{hwid}").text

    try:
        # Parse the JSON response to get the redirect URL
        response_json = json.loads(response)
        encoded_redirect_url = response_json.get('redirect')
        
        if encoded_redirect_url:
            # Apply LootLink Bypass if the redirect URL is from LootLink
            decoded_redirect_url = lootlink_bypass(encoded_redirect_url)
            
            if decoded_redirect_url.startswith('http'):
                # Perform further actions with the decoded URL
                print(f"Redirected to: {decoded_redirect_url}")
            
            # Now proceed with extracting the token as before
            unquoted_url = unquote(decoded_redirect_url)
            pattern = r"r=([^&]+)"
            match = re.search(pattern, unquoted_url)
            if match:
                encoded_url = match.group(1)
                
                if is_base64(encoded_url):
                    decoded_url = decode_base64_url(encoded_url)

                    # Extract the API token from the decoded URL
                    token_pattern = r"&tk=(\w{4})"
                    token_match = re.search(token_pattern, decoded_url)
                    if token_match:
                        api_token = token_match.group(1)

                        # Send a PUT request with the API token
                        session.put(f"https://api-gateway.platoboost.com/v1/sessions/auth/8/{hwid}/{api_token}")
                        # Get the final response with the key
                        get_response = session.get(f"https://api-gateway.platoboost.com/v1/authenticators/8/{hwid}")
                        get_response.raise_for_status()

                        # Extract and return the key from the final response
                        final_response_json = json.loads(get_response.text)
                        key = final_response_json.get('key')
                        return f"Key: {key}"

        return "Failed to retrieve key. Invalid or unexpected response."

    except json.JSONDecodeError:
        return "Error decoding JSON response."

    except Exception as e:
        return f"An error occurred: {str(e)}"

# Example usage of the function
hwid = "your_hwid_here"  # Replace with your HWID
result = get_delta_key(hwid)
print(result)
