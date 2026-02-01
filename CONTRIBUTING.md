# Contributing

Thank you for your interest in contributing to this MCP App Template!

## How to Contribute

### Reporting Issues

- Check existing issues before creating a new one
- Provide clear reproduction steps
- Include your environment details (Node.js version, Python version, OS)

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Run the build to ensure everything works:
   ```bash
   pnpm install
   pnpm run build
   ```
5. Commit your changes with a clear message
6. Push to your fork and submit a pull request

### Development Setup

```bash
# Full setup (installs deps, builds, runs tests)
./setup.sh

# Or manually:
pnpm install
cd server && python3 -m venv .venv && .venv/bin/pip install -e ".[dev]" && cd ..
pnpm run build
pnpm run test
```

### Code Style

- TypeScript/React: Follow existing patterns in the codebase
- Python: Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add comments for complex logic

### Adding New Widget Examples

If you'd like to contribute a new widget example:

1. Create a new directory in `src/` (e.g., `src/my-widget/`)
2. Add `index.tsx` and `App.tsx` following the existing patterns
3. Add the widget name to `build-all.mts`
4. Add corresponding tool handlers in `server/main.py`
5. Update the README if needed

## Questions?

Feel free to open an issue for questions or discussions.
