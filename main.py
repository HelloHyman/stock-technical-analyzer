"""
Main entry point for the Stock Analysis Application
"""

import signal
import sys
import flet as ft

from src.config.dependencies import YFINANCE_AVAILABLE, PLOTLY_AVAILABLE
from src.ui.main_app import StockAnalyzerApp


def main(page) -> None:
    """Main application entry point."""
    
    # Check dependencies first
    if not YFINANCE_AVAILABLE:
        snack_bar = ft.SnackBar(
            content=ft.Text("yfinance is required but not installed. Please install it with: pip install yfinance"),
            bgcolor=ft.Colors.RED
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
        return

    if not PLOTLY_AVAILABLE:
        snack_bar = ft.SnackBar(
            content=ft.Text("Plotly is required but not installed. Please install it with: pip install plotly"),
            bgcolor=ft.Colors.RED
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()
        return

    try:
        app = StockAnalyzerApp(page)
        
        # Set focus to symbol field
        if app.symbol_field:
            app.symbol_field.focus()
        
        # Handle window closing and application shutdown
        def on_disconnect():
            try:
                print("Application is shutting down...")
                app.cleanup()
                print("Cleanup completed successfully.")
            except Exception as e:
                print(f"Error during cleanup: {e}")
        
        # Set up disconnect handler
        page.on_disconnect = on_disconnect
        
        # Handle page close event
        def on_page_close():
            try:
                print("Page is closing...")
                app.cleanup()
            except Exception as e:
                print(f"Error during page close: {e}")
        
        # Register atexit handler as final cleanup
        import atexit
        atexit.register(lambda: app.cleanup() if 'app' in locals() else None)
        
    except Exception as e:
        print(f"Application startup error: {e}")
        snack_bar = ft.SnackBar(
            content=ft.Text(f"Failed to start application: {e}"),
            bgcolor=ft.Colors.RED
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()


def main_entry():
    """Main entry point for the application"""
    # Set up signal handlers in the main thread
    import signal
    import sys
    
    def signal_handler(signum, frame):
        print(f"\nReceived signal {signum}. Shutting down gracefully...")
        sys.exit(0)
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal
    
    try:
        print("Starting Stock Analysis Application...")
        ft.app(target=main)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user. Shutting down gracefully...")
    except Exception as e:
        print(f"Error starting application: {e}")
        print("Press Enter to exit...")
        try:
            input()
        except KeyboardInterrupt:
            print("\nForced exit.")
    finally:
        print("Application has closed.")


if __name__ == "__main__":
    main_entry()
