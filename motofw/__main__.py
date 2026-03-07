"""Allow ``python -m motofw`` to invoke the CLI."""

from motofw.src.cli.commands import main

if __name__ == "__main__":
    raise SystemExit(main())
