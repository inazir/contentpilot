import sys
from pathlib import Path

# Ensure repo root is on sys.path when running this script directly.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from shared.ai import (
    anthropic_complete,
    deepseek_complete,
    AIClientError,
)


def test_anthropic() -> None:
    print("\n=== Anthropic Test ===")
    try:
        result = anthropic_complete(
            prompt="Reply with exactly: Anthropic works",
            max_tokens=32,
            temperature=0.0,
        )
        print("Anthropic response:", result)

    except AIClientError as exc:
        print("Anthropic AIClientError:", str(exc))
        if exc.__cause__ is not None:
            print("Caused by:", repr(exc.__cause__))
        raise


def test_deepseek() -> None:
    print("\n=== DeepSeek Test ===")
    try:
        result = deepseek_complete(
            prompt="Reply with exactly: DeepSeek works",
            max_tokens=32,
            temperature=0.0,
        )
        print("DeepSeek response:", result)

    except AIClientError as exc:
        print("DeepSeek AIClientError:", str(exc))
        if exc.__cause__ is not None:
            print("Caused by:", repr(exc.__cause__))
        raise


def main() -> None:
    test_anthropic()
    test_deepseek()


if __name__ == "__main__":
    main()