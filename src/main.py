import uvicorn
import sys
import os


project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """Main entry point for the AutoMail Agent application."""
    print("🚀 Starting AutoMail Agent...")
    print("=" * 50)
    print("📧 AutoMail Agent - Gmail Automation Web Interface")
    print("🌐 Web Interface: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/api/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "src.api.app:app",  
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down AutoMail Agent...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 