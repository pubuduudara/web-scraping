FROM python:3.9
# Install dependencies and tools
RUN apt-get update -y && apt-get install -y build-essential
RUN apt install wget
# Install Google Chrome
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean


# Set up the working directory
RUN mkdir /web_scrape_common
WORKDIR /web_scrape_common

# Install Python dependencies
COPY requirements.txt /web_scrape_common/
RUN pip3 install -r requirements.txt

# Copy the rest of the application code
COPY . /web_scrape_common/

# Set the entry point
ENTRYPOINT ["python3", "main.py"]


