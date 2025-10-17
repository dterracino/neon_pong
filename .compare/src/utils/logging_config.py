"""
Logging configuration for Neon Pong using Rich handler
"""
import logging
from rich.logging import RichHandler
from src.utils.constants import LOG_LEVEL


def setup_logging():
    """
    Initialize logging with Rich handler for beautiful console output.
    
    This configures the root logger with:
    - Rich handler for colored, formatted output
    - Log level from constants.LOG_LEVEL
    - Pretty exception tracebacks
    - Module and function context
    """
    # Configure rich handler
    rich_handler = RichHandler(
        rich_tracebacks=True,  # Beautiful exception formatting
        tracebacks_show_locals=True,  # Show local variables in tracebacks
        markup=True,  # Allow rich markup in log messages
        show_time=True,  # Show timestamps
        show_level=True,  # Show log level
        show_path=True,  # Show file path
    )
    
    # Configure logging
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(message)s",  # Rich handler adds its own formatting
        datefmt="[%X]",  # Time format: HH:MM:SS
        handlers=[rich_handler]
    )
    
    # Optionally reduce verbosity of noisy libraries
    logging.getLogger("pygame").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    # Log that logging has been initialized
    logger = logging.getLogger(__name__)
    logger.debug("Logging system initialized with Rich handler")
    logger.debug("Log level: %s", logging.getLevelName(LOG_LEVEL))


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for the specified module.
    
    Args:
        name: Logger name, typically __name__ of the calling module
        
    Returns:
        Configured logger instance
        
    Example:
        logger = get_logger(__name__)
        logger.debug("This is a debug message")
        logger.info("This is an info message")
    """
    return logging.getLogger(name)
