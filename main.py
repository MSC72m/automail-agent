import uvicorn
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.logger import setup_logging, get_logger
from src.schemas.config import config

def main():
    """Main entry point for the AutoMail Agent application."""
    setup_logging()
    logger = get_logger(__name__)
    
    logger.info("🚀 Starting AutoMail Agent...")
    logger.info("=" * 50)
    logger.info("📧 AutoMail Agent - Gmail Automation Web Interface")
    logger.info(f"🌐 Web Interface: http://{config.host}:{config.port}")
    logger.info(f"📚 API Documentation: http://{config.host}:{config.port}/docs")
    logger.info(f"🔍 Health Check: http://{config.host}:{config.port}/health")
    logger.info(f"🔧 Environment: {config.environment.value}")
    logger.info(f"📊 Log Level: {config.log_level.value}")
    logger.info("=" * 50)
    
    try:
        uvicorn.run(
            "src.app:app",  
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