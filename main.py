#!/usr/bin/env python3
"""
RAG Application - Main Entry Point
Unified interface for CLI and Server modes
"""
import sys
import argparse


def main():
    """Main entry point with mode selection"""
    parser = argparse.ArgumentParser(
        description="RAG Application - Retrieval-Augmented Generation with Milvus & Ollama",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes:
  cli       Command-line interface (default)
  server    Start API server

CLI Examples:
  python main.py cli status
  python main.py cli ingest ./data/
  python main.py cli query
  python main.py cli query -q "What is AI?"

Server Examples:
  python main.py server
  python main.py server --port 8080
        """
    )
    
    parser.add_argument(
        'mode',
        nargs='?',
        default='cli',
        choices=['cli', 'server'],
        help='Operation mode (default: cli)'
    )
    
    # Parse known args to get mode
    args, remaining = parser.parse_known_args()
    
    if args.mode == 'server':
        # Server mode
        from src.rag_app.server import main as server_main
        sys.argv = ['server'] + remaining
        server_main()
    else:
        # CLI mode
        from src.rag_app.cli import main as cli_main
        sys.argv = ['cli'] + remaining
        cli_main()


if __name__ == "__main__":
    main()

# Made with Bob
