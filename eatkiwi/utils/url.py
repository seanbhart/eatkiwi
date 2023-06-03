

import logging
import requests


def send_post_request(url, data) -> bool:
    """
    Sends a request to the Kiwistand API to submit a message.

    Args:
        message_data (dict): A dictionary representing the message data to be sent.

    Returns:
        requests.Response: The response from the Kiwistand API.

    Raises:
        requests.exceptions.RequestException: If an error occurs while sending the request.

    """
    
    try:
        response = requests.post(url, json=data)
        status_code = response.status_code

        if status_code == 200:  # OK
            logging.info('Request was successful')
            return True
        elif status_code == 201:  # Created
            logging.info('Request was successful and a resource was created')
            return True
        elif status_code == 400:  # Bad Request
            logging.error(f'There was a problem with the request. Check the data sent: {response.text}')
            return False
        elif status_code == 401:  # Unauthorized
            logging.error(f'The request lacks valid authentication credentials: {response.text}')
            return False
        elif status_code == 403:  # Forbidden
            logging.error(f'The server understood the request but refuses to authorize it: {response.text}')
            return False
        elif status_code == 404:  # Not Found
            logging.error(f'The requested resource could not be found: {response.text}')
            return False
        elif status_code == 500:  # Internal Server Error
            logging.error(f'The server encountered an internal error: {response.text}')
            return False
        else:
            logging.error(f'Received status code that is not handled: {status_code}')
            return False
        
    except requests.exceptions.HTTPError as errh:
        logging.error(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        logging.error(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        logging.error(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        logging.error(f"Unexpected Error: {err}")
    except Exception as e:
        logging.error(f"[url] Failed sending request: {e}")
        raise Exception("[url] Failed sending request") from e
    return False