"""
Core functionality for downloading files from Google Drive.
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import pickle
import os.path
import io
from typing import Optional

class GDriveDownloader:
    """
    A class to handle Google Drive file downloads using the official API.
    """

    def __init__(self, credentials_path: str = 'credentials.json'):
        """
        Initialize the Google Drive downloader.

        Args:
            credentials_path (str): Path to the credentials.json file
        """
        self.SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        self.credentials_path = credentials_path
        self.service = self._get_service()

    def _get_service(self):
        """
        Authenticate and create Google Drive service.

        Returns:
            google.discovery.Resource: Authenticated Google Drive service
            
        Raises:
            TimeoutError: If authentication server doesn't respond
        """
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0, timeout=60)  # Add timeout

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return build('drive', 'v3', credentials=creds)

    def download_file(self, file_id: str, output_path: str) -> bool:
        """
        Download a file from Google Drive.

        Args:
            file_id (str): The ID of the file to download
            output_path (str): Where to save the downloaded file

        Returns:
            bool: True if download was successful, False otherwise
            
        Raises:
            ValueError: If file_id is empty or output_path is invalid
        """
        if not file_id or not output_path:
            raise ValueError("File ID and output path must be provided")
            
        try:
            # Get file metadata first
            file_metadata = self.get_file_metadata(file_id)
            if not file_metadata:
                return False
                
            print(f"Preparing to download: {file_metadata.get('name', 'Unknown file')}")
            print(f"File size: {int(file_metadata.get('size', 0) / 1024 / 1024):.2f} MB")

            request = self.service.files().get_media(fileId=file_id)
            file = io.BytesIO()
            downloader = MediaIoBaseDownload(file, request)
            done = False

            while not done:
                status, done = downloader.next_chunk()
                print(f"Download progress: {int(status.progress() * 100)}%", end='\r')

            print("\nDownload completed!")
            file.seek(0)
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(file.read())

            return True

        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return False

    def get_file_metadata(self, file_id: str) -> Optional[dict]:
        """
        Get metadata for a file.
    
        Args:
            file_id (str): The ID of the file
    
        Returns:
            Optional[dict]: File metadata containing:
                - id: File ID
                - name: File name
                - mimeType: File MIME type
                - size: File size in bytes
                - modifiedTime: Last modification time
                - owners: List of file owners
                - shared: Whether the file is shared
            
        Raises:
            ValueError: If file_id is empty
        """
        if not file_id:
            raise ValueError("File ID must be provided")
            
        try:
            return self.service.files().get(
                fileId=file_id, 
                fields='id, name, mimeType, size, modifiedTime, owners, shared'
            ).execute()
        except Exception as e:
            print(f"Error getting file metadata: {str(e)}")
            return None

    def format_metadata(self, metadata: dict) -> str:
        """
        Format file metadata into a readable string.

        Args:
            metadata (dict): File metadata from get_file_metadata

        Returns:
            str: Formatted metadata string
        """
        if not metadata:
            return "No metadata available"

        size_mb = float(metadata.get('size', 0)) / 1024 / 1024
        owners = ', '.join([owner['displayName'] for owner in metadata.get('owners', [])])

        return (
            f"File Name: {metadata.get('name', 'Unknown')}\n"
            f"Type: {metadata.get('mimeType', 'Unknown')}\n"
            f"Size: {size_mb:.2f} MB\n"
            f"Modified: {metadata.get('modifiedTime', 'Unknown')}\n"
            f"Owner(s): {owners}\n"
            f"Shared: {'Yes' if metadata.get('shared') else 'No'}"
        )