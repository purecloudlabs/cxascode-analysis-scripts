
class Config:
    """Configuration class to read environment variables"""
    
    def __init__(self):
        import os
        from pathlib import Path
        
        # Get file location from environment variable, default to current directory
        self.TERRAFORM_LOG_PATH = os.getenv('TERRAFORM_LOG_PATH', "")
        self.NORMALIZED_TERRAFORM_LOG_PATH = os.getenv('NORMALIZED_TERRAFORM_LOG_PATH', "")
        self.NORMALIZED_GENESYS_SDK_PATH = os.getenv('NORMALIZED_GENESYS_SDK_PATH', "")