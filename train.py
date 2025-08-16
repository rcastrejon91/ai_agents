"""Training script for real-time video generation."""

import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Train the AAPT model")
    parser.add_argument(
        "--config", type=str, required=True, help="Path to a YAML config file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="checkpoints",
        help="Directory to store model checkpoints",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    # TODO: load config and initialize model/training loop
    print(f"Starting training with config: {args.config}")
    print(f"Checkpoints will be saved to: {args.output}")


if __name__ == "__main__":
    main()
