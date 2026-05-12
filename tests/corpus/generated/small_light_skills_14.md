## Skills

### search_web
Search the internet for information on a topic.
- Input: query (string)
- Output: list of results with title, url, snippet

### read_url
Fetch and read the text content of a web page.
- Input: url (string)
- Output: page text (string, max 10000 chars)

### write_file
Write text to a file on disk.
- Input: path (string), content (string)
- Output: success boolean

### run_python
Execute a Python script and return stdout.
- Input: code (string)
- Output: stdout (string), stderr (string), exit_code (int)

### ask_human
Pause and ask the user a clarifying question.
- Input: question (string)
- Output: user's answer (string)

## Usage Rules

Call ask_human when you are unsure of intent. Do not guess and proceed on ambiguous tasks.

Call write_file only after confirming the destination path with the user.

Do not call run_python with code that makes network requests unless the user explicitly asked for it.
