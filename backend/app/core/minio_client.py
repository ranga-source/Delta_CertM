"""
MinIO Client Module
==================
This module provides a wrapper around the MinIO Python client for
managing certificate document storage in a self-hosted S3-compatible service.

Key Features:
- Automatic bucket creation on initialization
- File upload with metadata
- Presigned URL generation for secure downloads
- File deletion with error handling
- Content type management

MinIO vs S3:
- MinIO is S3-compatible but self-hosted
- No AWS costs, full control over data
- Same API as AWS S3 (easy migration if needed)
"""

from minio import Minio
from minio.error import S3Error
from app.core.config import settings
from datetime import timedelta
from io import BytesIO
import logging

# Setup logging
logger = logging.getLogger(__name__)


class MinIOClient:
    """
    MinIO Client Wrapper Class
    
    This class encapsulates all MinIO operations for certificate storage.
    It provides a clean interface for file management operations.
    
    Attributes:
        client (Minio): MinIO client instance
        bucket_name (str): Name of the bucket for certificate storage
    
    Usage:
        minio_client = MinIOClient()
        object_name = minio_client.upload_file(file_data, "cert.pdf", "application/pdf")
        download_url = minio_client.get_presigned_url(object_name)
    """
    
    def __init__(self):
        """
        Initialize MinIO client and ensure bucket exists.
        
        Process:
            1. Create MinIO client with credentials from settings
            2. Check if certificate bucket exists
            3. Create bucket if it doesn't exist
            4. Log initialization status
        """
        logger.info(f"Initializing MinIO client: {settings.EFFECTIVE_MINIO_ENDPOINT}")
        
        # Create MinIO client instance
        self.client = Minio(
            settings.EFFECTIVE_MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE  # Use HTTPS in production
        )
        
        self.bucket_name = settings.MINIO_BUCKET_NAME
        
        # Ensure the bucket exists
        self._ensure_bucket()
        
        logger.info(f"MinIO client initialized successfully. Bucket: {self.bucket_name}")
    
    def _ensure_bucket(self):
        """
        Create bucket if it doesn't exist.
        
        This private method is called during initialization to ensure
        the certificates bucket is available for file operations.
        
        Note:
            Bucket names must be unique and follow DNS naming conventions:
            - Lowercase letters, numbers, hyphens
            - 3-63 characters long
        """
        try:
            # Check if bucket already exists
            if not self.client.bucket_exists(self.bucket_name):
                logger.info(f"Bucket '{self.bucket_name}' not found. Creating...")
                
                # Create the bucket
                self.client.make_bucket(self.bucket_name)
                
                logger.info(f"Bucket '{self.bucket_name}' created successfully!")
            else:
                logger.info(f"Bucket '{self.bucket_name}' already exists.")
                
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {str(e)}")
            raise
    
    def upload_file(
        self, 
        file_data: bytes, 
        object_name: str, 
        content_type: str = "application/pdf"
    ) -> str:
        """
        Upload a file to MinIO storage.
        
        This method uploads certificate documents to MinIO with proper
        content type and metadata.
        
        Args:
            file_data (bytes): Binary content of the file to upload
            object_name (str): Path/name for the object in MinIO
                              Format: "certificates/tenant_id/device_id/filename.pdf"
            content_type (str): MIME type of the file (default: application/pdf)
        
        Returns:
            str: The object name (path) where the file was stored
        
        Raises:
            S3Error: If upload fails due to MinIO errors
        
        Example:
            >>> file_bytes = open("cert.pdf", "rb").read()
            >>> path = minio_client.upload_file(
            ...     file_bytes, 
            ...     "certificates/tenant-123/device-456/fcc_cert.pdf",
            ...     "application/pdf"
            ... )
            >>> print(path)
            "certificates/tenant-123/device-456/fcc_cert.pdf"
        """
        try:
            # Convert bytes to BytesIO stream (required by MinIO)
            file_stream = BytesIO(file_data)
            file_size = len(file_data)
            
            logger.info(f"Uploading file to MinIO: {object_name} ({file_size} bytes)")
            
            # Upload file to MinIO
            self.client.put_object(
                self.bucket_name,
                object_name,
                file_stream,
                length=file_size,
                content_type=content_type
            )
            
            logger.info(f"File uploaded successfully: {object_name}")
            return object_name
            
        except S3Error as e:
            logger.error(f"Error uploading file to MinIO: {str(e)}")
            raise
    
    def get_presigned_url(
        self, 
        object_name: str, 
        expires_seconds: int = 3600
    ) -> str:
        """
        Generate a presigned URL for secure file download.
        
        Presigned URLs allow temporary access to private files without
        exposing credentials. The URL expires after the specified duration.
        
        Args:
            object_name (str): Path to the object in MinIO
            expires_seconds (int): URL validity duration in seconds (default: 1 hour)
        
        Returns:
            str: Presigned URL for downloading the file
        
        Security:
            - URLs are time-limited (expire after specified duration)
            - No credentials required for download
            - Perfect for sharing certificates with limited access
        
        Example:
            >>> url = minio_client.get_presigned_url("certificates/cert.pdf", 7200)
            >>> # URL is valid for 2 hours (7200 seconds)
            >>> print(url)
            "http://localhost:9000/certificates/cert.pdf?X-Amz-Algorithm=..."
        """
        try:
            logger.info(f"Generating presigned URL for: {object_name}")
            
            # Generate presigned GET URL
            url = self.client.presigned_get_object(
                self.bucket_name,
                object_name,
                expires=timedelta(seconds=expires_seconds)
            )
            
            logger.info(f"Presigned URL generated (expires in {expires_seconds}s)")
            return url
            
        except S3Error as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise
    
    def delete_file(self, object_name: str) -> bool:
        """
        Delete a file from MinIO storage.
        
        This method removes a certificate document from MinIO.
        Use with caution - deletion is permanent!
        
        Args:
            object_name (str): Path to the object to delete
        
        Returns:
            bool: True if deletion successful, False otherwise
        
        Note:
            This should typically be called when:
            - A compliance record is deleted
            - A certificate is being replaced with a new version
            - Tenant data cleanup is required
        
        Example:
            >>> success = minio_client.delete_file("certificates/old_cert.pdf")
            >>> if success:
            ...     print("Certificate deleted successfully")
        """
        try:
            logger.info(f"Deleting file from MinIO: {object_name}")
            
            # Remove object from MinIO
            self.client.remove_object(self.bucket_name, object_name)
            
            logger.info(f"File deleted successfully: {object_name}")
            return True
            
        except S3Error as e:
            logger.error(f"Error deleting file from MinIO: {str(e)}")
            return False
    
    def file_exists(self, object_name: str) -> bool:
        """
        Check if a file exists in MinIO.
        
        Args:
            object_name (str): Path to the object to check
        
        Returns:
            bool: True if file exists, False otherwise
        
        Example:
            >>> if minio_client.file_exists("certificates/cert.pdf"):
            ...     print("Certificate found")
        """
        try:
            # Try to get object metadata (stat_object)
            self.client.stat_object(self.bucket_name, object_name)
            return True
        except S3Error:
            return False


# ============================================
# Global MinIO Client Instance
# ============================================
"""
Create a single MinIO client instance to be used throughout the application.
This follows the singleton pattern for efficient resource usage.

Usage:
    from app.core.minio_client import minio_client
    
    # Upload a file
    path = minio_client.upload_file(file_data, "cert.pdf", "application/pdf")
    
    # Get download URL
    url = minio_client.get_presigned_url(path)
"""
minio_client = MinIOClient()


