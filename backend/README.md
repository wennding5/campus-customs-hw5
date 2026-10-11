# Campus Customs backend

From this directory, install `requirements.txt` and run exactly:

```bash
uvicorn main:app --reload --port 8000
```

The API uses the five-agent PydanticAI team and the MCP server. It never opens SQLite directly. Shop reads, guarded approvals, and reset operations are routed through MCP; the original database remains untouched.
