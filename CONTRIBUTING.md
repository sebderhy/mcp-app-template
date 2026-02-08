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
2. Add `index.tsx` and `App.tsx` following the existing patterns (auto-discovered by the build)
3. Create `server/widgets/my_widget.py` with `WIDGET`, `INPUT_MODEL`, and `handle()` exports (auto-discovered by the server)
4. Run `pnpm run build && pnpm run test`
5. Update the README if needed

## Roadmap & Help Wanted

See the [Roadmap](README.md#roadmap) in the README for planned features.

One area where contributions would be especially impactful: **LLM-based test evaluation**. The automated grading tests (`server/tests/test_*.py`) currently use heuristic checks — keyword matching, regex patterns, length thresholds — which can produce false positives/negatives for edge cases. Replacing these with LLM-based evaluation would make the grading far more accurate. Look for `TODO: Improve with LLM` comments across the test files for specific opportunities.

## Questions?

Feel free to open an issue for questions or discussions.
