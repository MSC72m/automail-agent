import uvicorn
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.schemas.config import config
from src.utils.logger import setup_logging, get_logger

def main():
    """Main entry point for the AutoMail Agent application."""
    # Setup logging first
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info("🚀 Starting AutoMail Agent...")
    print("=" * 50)
    print("📧 AutoMail Agent - Gmail Automation Web Interface")
    print(f"🌐 Web Interface: http://{config.host}:{config.port}")
    print(f"📚 API Documentation: http://{config.host}:{config.port}/docs")
    print(f"🔍 Health Check: http://{config.host}:{config.port}/health")
    print(f"🔧 Environment: {config.environment.value}")
    print(f"📊 Log Level: {config.log_level.value}")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "src.api.app:app",  
            host=config.host,
            port=config.port,
            reload=config.reload,
            log_level=config.log_level.value.lower()
        )
    except KeyboardInterrupt:
        logger.info("👋 Shutting down AutoMail Agent...")
    except Exception as e:
        logger.error(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 