# Migrating to Claude 4.x

This page provides guidance on migrating from Claude 3.7 models to Claude 4 models (e.g., Opus 4.1 and Sonnet 4.5).

In most cases, you can switch to Claude 4 models with minimal changes:

1. Update your model name:
   * From: `claude-3-7-sonnet-20250219`
   * To: `claude-sonnet-4-5-20250929` (or `claude-opus-4-1-20250805`)

2. Existing API calls should continue to work without modification, although API behavior has changed slightly (see [API release notes](/en/release-notes/api) for details).

## What's new in Claude 4

### New refusal stop reason

Claude 4 models introduce a new `refusal` stop reason for content that the model declines to generate for safety reasons, due to the increased intelligence of Claude 4 models:

```json  theme={null}
{"id":"msg_014XEDjypDjFzgKVWdFUXxZP",
"type":"message",
"role":"assistant",
"model":"claude-sonnet-4-5",
"content":[{"type":"text","text":"I would be happy to assist you. You can "}],
"stop_reason":"refusal",
"stop_sequence":null,
"usage":{"input_tokens":564,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":22}
}
```

When migrating to Claude 4.x, you should update your application to [handle `refusal` stop reasons](/en/docs/test-and-evaluate/strengthen-guardrails/handle-streaming-refusals).

### Summarized thinking

With extended thinking enabled, the Messages API for Claude 4 models returns a summary of Claude's full thinking process. Summarized thinking provides the full intelligence benefits of extended thinking, while preventing misuse.

While the API is consistent across Claude 3.7 and 4 models, streaming responses for extended thinking might return in a "chunky" delivery pattern, with possible delays between streaming events.

<Note>
  Summarization is processed by a different model than the one you target in your requests. The thinking model does not see the summarized output.
</Note>

For more information, see the [Extended thinking documentation](/en/docs/build-with-claude/extended-thinking#summarized-thinking).

### Interleaved thinking

Claude 4 models support interleaving tool use with extended thinking, allowing for more natural conversations where tool uses and responses can be mixed with regular messages.

<Note>
  Interleaved thinking is in beta. To enable interleaved thinking, add [the beta header](/en/api/beta-headers) `interleaved-thinking-2025-05-14` to your API request.
</Note>

For more information, see the [Extended thinking documentation](/en/docs/build-with-claude/extended-thinking#interleaved-thinking).

### Behavioral differences

Claude 4 models, particularly Sonnet 4.5, have notable behavioral changes that may affect how you structure prompts:

#### Communication style changes

* **More concise and direct**: Claude 4 models communicate more efficiently, with less verbose explanations
* **More natural tone**: Responses are slightly more conversational and less machine-like
* **Efficiency-focused**: May skip detailed summaries after completing actions to maintain workflow momentum (you can prompt for more detail if needed)

#### Instruction following

Claude 4 models are trained for precise instruction following and require more explicit direction:

* **Be explicit about actions**: Use direct language like "Make these changes" or "Implement this feature" rather than "Can you suggest changes" if you want Claude to take action
* **State desired behaviors clearly**: Claude will follow instructions precisely, so being specific about what you want helps achieve better results

For comprehensive guidance on working with these models, see [Claude 4 prompt engineering best practices](/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices).

### Updated text editor tool

The text editor tool has been updated for Claude 4 models with the following changes:

* **Tool type**: `text_editor_20250728`
* **Tool name**: `str_replace_based_edit_tool`
* The `undo_edit` command is no longer supported.

<Note>
  The `str_replace_editor` text editor tool remains the same for Claude Sonnet 3.7.
</Note>

If you're migrating from Claude Sonnet 3.7 and using the text editor tool:

```python  theme={null}
# Claude Sonnet 3.7
tools=[
    {
        "type": "text_editor_20250124",
        "name": "str_replace_editor"
    }
]

# Claude 4
tools=[
    {
        "type": "text_editor_20250728",
        "name": "str_replace_based_edit_tool"
    }
]
```

For more information, see the [Text editor tool documentation](/en/docs/agents-and-tools/tool-use/text-editor-tool).

### Updated code execution tool

If you're using the code execution tool, ensure you're using the latest version `code_execution_20250825`, which adds Bash commands and file manipulation capabilities.

The legacy version `code_execution_20250522` (Python only) is still available but not recommended for new implementations.

For migration instructions, see the [Code execution tool documentation](/en/docs/agents-and-tools/tool-use/code-execution-tool#upgrade-to-latest-tool-version).

## Removed features

### Token-efficient tool use no longer supported

[Token-efficient tool use](/en/docs/agents-and-tools/tool-use/token-efficient-tool-use) is only available in Claude Sonnet 3.7.

If you're migrating from Claude Sonnet 3.7 and using token-efficient tool use, remove the `token-efficient-tools-2025-02-19` [beta header](/en/api/beta-headers) from your requests.

The `token-efficient-tools-2025-02-19` beta header can still be included in Claude 4 requests, but it will have no effect.

### Extended output no longer supported

The `output-128k-2025-02-19` [beta header](/en/api/beta-headers) for extended output is only available in Claude Sonnet 3.7.

If you're migrating from Claude Sonnet 3.7, remove `output-128k-2025-02-19` from your requests.

The `output-128k-2025-02-19` beta header can still be included in Claude 4 requests, but it will have no effect.

## Performance considerations

### Choose Claude Sonnet 4.5 for:

* **Long-running agents**: Best-in-class for autonomous agents that work independently for extended periods
* **Coding tasks**: Our strongest coding model with advanced planning and security engineering
* **Large context workflows**: Enhanced context management with memory tool and context editing capabilities
* **Most use cases**: Latest model with the best balance of capability and performance

### Choose Claude Opus 4.1 for:

* **Specialized complex tasks**: When you need exceptional depth of analysis
* **Tasks where speed is not critical**: Slower but more thorough than Sonnet models

### Extended thinking recommendations

Claude 4 models, particularly Sonnet 4.5, show significant performance improvements when using [extended thinking](/en/docs/build-with-claude/extended-thinking) for coding and complex reasoning tasks. Extended thinking is **disabled by default** but we recommend enabling it for demanding work.

**Enabling extended thinking:**

* **API**: Include the `thinking` parameter in your requests:
  ```python  theme={null}
  response = client.messages.create(
      model="claude-sonnet-4-5",
      max_tokens=16000,
      thinking={
          "type": "enabled",
          "budget_tokens": 10000
      },
      messages=[...]
  )
  ```

* **Claude Code**: Set the `MAX_THINKING_TOKENS` environment variable in your [settings](/en/docs/claude-code/settings):
  ```json  theme={null}
  {
    "env": {
      "MAX_THINKING_TOKENS": "10000"
    }
  }
  ```

**Important**: Extended thinking impacts [prompt caching](/en/docs/build-with-claude/prompt-caching#caching-with-thinking-blocks) efficiency. When non-tool-result content is added to a conversation, thinking blocks are stripped from cache, which can increase costs in multi-turn conversations. We recommend enabling thinking when the performance benefits outweigh the caching trade-off.

## Migration checklist

* [ ] Update model id in your API calls
* [ ] Test existing requests (should work without changes)
* [ ] Review [Claude 4 prompt engineering best practices](/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) to understand behavioral changes and prompt optimization
* [ ] Update prompts to be more explicit about desired actions (e.g., "Implement this" vs "Can you suggest")
* [ ] Adjust expectations for communication style (more concise, may need to prompt for detailed summaries if desired)
* [ ] Remove `token-efficient-tools-2025-02-19` beta header if applicable
* [ ] Remove `output-128k-2025-02-19` beta header if applicable
* [ ] Handle new `refusal` stop reason
* [ ] Update text editor tool type and name if using it
* [ ] Remove any code that uses the `undo_edit` command
* [ ] If using code execution tool: Upgrade to latest version (`code_execution_20250825`) if still on legacy version
* [ ] Explore new tool interleaving capabilities with extended thinking
* [ ] If using Sonnet 4.5: Review [What's new in Sonnet 4.5](/en/docs/about-claude/models/whats-new-sonnet-4-5) for additional features
* [ ] If using Sonnet 4.5: Handle `model_context_window_exceeded` stop reason
* [ ] If using Sonnet 4.5: Consider enabling memory tool for long-running agents (beta)
* [ ] If using Sonnet 4.5: Consider using automatic tool call clearing for context editing (beta)
* [ ] For agentic workflows: Leverage state tracking capabilities with structured state files (JSON recommended for structured data)
* [ ] Test in development before production deployment

## Need help?

* Check our [API documentation](/en/api/overview) for detailed specifications.
* Review [model capabilities](/en/docs/about-claude/models/overview) for performance comparisons.
* Review [API release notes](/en/release-notes/api) for API updates.
* Contact support if you encounter any issues during migration.
