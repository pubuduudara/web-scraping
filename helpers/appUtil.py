import time
import re


class AppUtil:

    @staticmethod
    def sleep(seconds):
        """
            Pauses the execution of the program for the specified number of seconds.

            This function uses the time.sleep method to halt the program's execution for a given duration, allowing for
            controlled delays.

            Args:
                seconds (int or float): The number of seconds to pause the program.
            """
        time.sleep(seconds)

    @staticmethod
    def remove_extra_spaces(text):
        """
            Removes extra spaces from a given string.

            This function replaces multiple consecutive whitespace characters in the input text with a single space and
            trims leading and trailing whitespace.

            Args:
                text (str): The input string from which to remove extra spaces.

            Returns:
                str: The cleaned string with extra spaces removed.
            """
        cleaned_text = re.sub(r'\s+', ' ', text)
        return cleaned_text.strip()

    @staticmethod
    def sanitize_data(value):
        """
            Sanitizes the input data by returning the value if it's not an empty string,
            otherwise returns None.

            Args:
                value (str): The data to be sanitized.

            Returns:
                str | None: The sanitized data (original value if not empty), otherwise None.
            """
        return value if value != '' else None
