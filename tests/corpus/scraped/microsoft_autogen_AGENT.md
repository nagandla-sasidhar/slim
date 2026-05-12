# AutoGen — Multi-Agent Conversation Framework

## Agent Configuration for This Project

This file configures the AutoGen agents used in this project's automated software engineering workflow.

## Agents

### UserProxyAgent

Acts as the human proxy in the conversation. Executes code locally in a sandboxed Docker container.

```python
user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "") and
        x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "workspace",
        "use_docker": "python:3.11-slim",
    },
)
```

### AssistantAgent

The primary coding assistant. Uses GPT-4o by default.

```python
assistant = AssistantAgent(
    name="Assistant",
    llm_config={
        "config_list": config_list,
        "temperature": 0,
        "cache_seed": 42,
    },
    system_message="""You are a helpful AI assistant. Solve tasks using Python code.
Reply TERMINATE when the task is complete.""",
)
```

### GroupChatManager

Manages multi-agent conversations for complex tasks.

```python
groupchat = GroupChat(
    agents=[user_proxy, coder, reviewer, pm],
    messages=[],
    max_round=12,
    speaker_selection_method="round_robin",
)
manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)
```

## LLM Configuration

Model configurations are in `OAI_CONFIG_LIST`. Set the environment variable `OAI_CONFIG_LIST` to a JSON array:

```json
[
    {"model": "gpt-4o", "api_key": "your-key"},
    {"model": "claude-3-7-sonnet", "api_key": "your-key", "api_type": "anthropic"}
]
```

## Termination Conditions

Conversations end when:
- An agent sends a message ending with `TERMINATE`
- `max_consecutive_auto_reply` is reached (default 10)
- All subtasks are marked complete

## Code Execution Safety

- All generated code runs in Docker — never on the host directly
- Network access is disabled in the execution container unless required
- Working directory is isolated per session in `workspace/{session_id}/`

## Logging

Set `autogen.runtime_logging.start()` to log all messages to SQLite for debugging. Log files are in `logs/`.
