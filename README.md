# Simple Media Transmission Test

## Project Name
Simple Media Transmission Test

## Project Purpose
This project aims to test the performance of video transmission between two devices in an unstable wireless communication environment.

## Project Structure
- `src/transmitter.py`: Code for the transmitter, which uses an unstable wireless communication protocol to send video files.
- `src/receiver.py`: Code for the receiver, which receives video data from the transmitter and displays the video in real-time.

## Usage
1. Ensure `pipenv` is installed.
2. Run the following command in the project root directory to install dependencies:
   ```
   pipenv install --deploy --ignore-pipfile
   ```
3. Start the transmitter:
   ```
   pipenv run python src/transmitter.py
   ```
4. Start the receiver:
   ```
   pipenv run python src/receiver.py
   ```
