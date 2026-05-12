# E2B — Code Execution Sandbox for AI Agents

## Agent Configuration

E2B provides secure cloud sandboxes for running AI-generated code. This AGENT.md describes how agents should use E2B sandboxes.

## Sandbox Lifecycle

```python
from e2b_code_interpreter import Sandbox

# Create sandbox (takes ~200ms cold start)
sbx = Sandbox()

# Execute code
execution = sbx.run_code("print('hello')")
print(execution.text)   # stdout
print(execution.error)  # stderr (if any)

# Close sandbox when done
sbx.kill()

# Or use as context manager
with Sandbox() as sbx:
    result = sbx.run_code("1 + 1")
```

## For AI Agents Using E2B

### Code execution rules

- Always use `Sandbox()` — never execute AI-generated code outside a sandbox
- Sandboxes are ephemeral — don't rely on state persisting between separate `Sandbox()` calls
- Files uploaded to a sandbox are gone after `sbx.kill()`
- Max execution time: 30s per `run_code()` call (configurable up to 300s)

### Handling results

```python
execution = sbx.run_code(code)

# Always check for errors before using results
if execution.error:
    # Feed error back to LLM for correction
    error_info = f"Error: {execution.error.name}: {execution.error.value}"
    error_info += f"\nTraceback:\n{execution.error.traceback}"
else:
    result = execution.text
```

### File operations

```python
# Upload a file to the sandbox
sbx.files.write("data.csv", open("local_data.csv", "rb").read())

# Run code that uses the file
sbx.run_code("import pandas as pd; df = pd.read_csv('data.csv'); print(df.head())")

# Download results
chart_data = sbx.files.read("output.png")
```

### Jupyter-style cells

E2B sandboxes support stateful Jupyter-style execution. Variables persist between `run_code()` calls within the same sandbox:

```python
sbx.run_code("x = 42")
result = sbx.run_code("print(x)")  # prints 42
```

## Sandbox Templates

Use custom templates for sandboxes with pre-installed dependencies:

```python
sbx = Sandbox(template="data-science")  # pandas, numpy, matplotlib pre-installed
```

Build custom templates with the E2B CLI:
```bash
e2b template build --dockerfile Dockerfile --name my-template
```

## Security Notes

- Sandboxes have no internet access by default — enable with `Sandbox(internet=True)` (use with caution)
- Sandboxes run as a non-root user
- File system access is isolated — sandboxes cannot access host files
- Secrets should never be passed as code strings — use environment variables: `Sandbox(envs={"API_KEY": key})`
