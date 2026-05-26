import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from shared.ai import (
    anthropic_complete,
    deepseek_complete,
    AIClientError,
    get_ai_config,
    ai_complete,
)


def test_direct_providers() -> None:
    """
    Tests direct provider calls using models from env config.
    """

    print("\n=== Direct Provider Tests ===")

    cfg = get_ai_config("default")

    print(f"Default provider:          {cfg.provider}")
    print(f"Default model:             {cfg.model}")
    print(f"Fallback provider:         {cfg.fallback_provider}")
    print(f"Fallback model:            {cfg.fallback_model}")

    # --------------------------------------------------------
    # Test default provider directly
    # --------------------------------------------------------

    try:
        if cfg.provider == "anthropic":
            result = anthropic_complete(
                prompt="Reply with exactly: Anthropic direct works",
                model=cfg.model,
                max_tokens=32,
                temperature=0.0,
            )

        elif cfg.provider == "deepseek":
            result = deepseek_complete(
                prompt="Reply with exactly: DeepSeek direct works",
                model=cfg.model,
                max_tokens=32,
                temperature=0.0,
            )

        else:
            raise ValueError(f"Unsupported provider: {cfg.provider}")

        print("Default provider response:", result)

    except AIClientError as exc:
        print("Default provider failed:", str(exc))
        if exc.__cause__ is not None:
            print("Caused by:", repr(exc.__cause__))

    # --------------------------------------------------------
    # Test fallback provider directly
    # --------------------------------------------------------

    try:
        if cfg.fallback_provider == "anthropic":
            result = anthropic_complete(
                prompt="Reply with exactly: Anthropic fallback works",
                model=cfg.fallback_model,
                max_tokens=32,
                temperature=0.0,
            )

        elif cfg.fallback_provider == "deepseek":
            result = deepseek_complete(
                prompt="Reply with exactly: DeepSeek fallback works",
                model=cfg.fallback_model,
                max_tokens=32,
                temperature=0.0,
            )

        else:
            raise ValueError(
                f"Unsupported fallback provider: {cfg.fallback_provider}"
            )

        print("Fallback provider response:", result)

    except AIClientError as exc:
        print("Fallback provider failed:", str(exc))
        if exc.__cause__ is not None:
            print("Caused by:", repr(exc.__cause__))


def test_router() -> None:
    """
    Tests the shared router abstraction.
    """

    print("\n=== Router Test ===")

    cfg = get_ai_config("default")

    print(f"Router provider:           {cfg.provider}")
    print(f"Router model:              {cfg.model}")
    print(f"Router fallback provider:  {cfg.fallback_provider}")
    print(f"Router fallback model:     {cfg.fallback_model}")
    print(f"Router max tokens:         {cfg.max_tokens}")
    print(f"Router temperature:        {cfg.temperature}")

    try:
        result = ai_complete(
            cfg,
            prompt="Reply with exactly: Router works",
            system="You are a test assistant. Follow instructions exactly.",
        )

        print("Router response:", result)

    except AIClientError as exc:
        print("Router failed:", str(exc))
        if exc.__cause__ is not None:
            print("Caused by:", repr(exc.__cause__))
        raise


def main() -> None:
    test_direct_providers()
    test_router()


if __name__ == "__main__":
    main()