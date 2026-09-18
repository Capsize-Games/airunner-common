"""Field-shape regression test for LLMRequest (issue airunner#2221).

Desktop's and services' pre-merge ``LLMRequest`` dataclasses each carried
private fields the other side didn't. Those deliberately stay on each
distribution's own subclass; this module is the *contract subset* both
sides share, and this test pins it so:

* a future edit can't silently drop or rename a shared field (the failure
  mode is a field read via ``getattr``/``hasattr`` quietly changing
  result, not an import error), and
* a future edit can't quietly union a distribution-private field into the
  base -- doing so is *not* behavior-neutral for services, whose legacy
  API layer gates untrusted input on ``hasattr(llm_request, key)`` (see
  the module docstring and airunner#2221).
"""

from __future__ import annotations

import dataclasses

from airunner_common.contract_enums import MessageRole
from airunner_common.llm_request import LLMRequest as SharedLLMRequest

# The fields both distributions declared, with the default each had on
# both sides before the merge.
_SHARED_FIELDS = {
    "do_sample": True,
    "early_stopping": True,
    "eta_cutoff": 200,
    "length_penalty": 1.0,
    "max_new_tokens": 8192,
    "min_length": 1,
    "no_repeat_ngram_size": 3,
    "num_beams": 1,
    "num_return_sequences": 1,
    "repetition_penalty": 1.15,
    "temperature": 0.7,
    "top_k": 20,
    "top_p": 0.8,
    "use_cache": True,
    "do_tts_reply": True,
    "node_id": None,
    "use_memory": True,
    "ephemeral": False,
    "tool_categories": [],
    "role": MessageRole.USER,
    "system_prompt": None,
    "response_format": None,
    "rag_files": [],
    "ephemeral_conversation": False,
    "include_mood": None,
    "include_datetime": None,
    "include_style": None,
    "include_memory": None,
    "include_ui_context": None,
    "enable_thinking": None,
    "reasoning_effort": None,
    "model": "",
    "model_service": None,
    "api_model": None,
    "dtype": None,
    "force_tool": None,
    "images": [],
}

# Fields that must NOT live on the shared contract class: each side owns
# these privately on its own subclass.
_DESKTOP_PRIVATE_FIELDS = {
    "final_system_prompt",
    "rewritten_prompt",
    "preprocessed_primary_tool",
    "planner_mode",
    "planner_tool_hints",
    "attached_document_capabilities",
    "attached_document_total_tokens",
    "attached_document_total_characters",
    "document_query_intent",
    "document_summary_focus",
    "document_primary_tool",
    "document_answer_mode",
    "request_plan",
}
_SERVICES_PRIVATE_FIELDS = {
    "gguf_runtime_profile",
    "client_tools",
    "client_tool_choice",
    "raw_mode",
}


def test_every_shared_field_is_present_with_its_default():
    request = SharedLLMRequest()
    for name, default in _SHARED_FIELDS.items():
        assert hasattr(request, name), f"missing shared field: {name}"
        assert getattr(request, name) == default, (
            f"{name} default changed: expected {default!r}, "
            f"got {getattr(request, name)!r}"
        )


def test_field_set_is_exactly_the_shared_contract():
    names = {f.name for f in dataclasses.fields(SharedLLMRequest)}
    assert names == set(_SHARED_FIELDS)


def test_distribution_private_fields_are_not_on_the_shared_contract():
    names = {f.name for f in dataclasses.fields(SharedLLMRequest)}
    leaked = names & (_DESKTOP_PRIVATE_FIELDS | _SERVICES_PRIVATE_FIELDS)
    assert leaked == set(), (
        "distribution-private fields must stay on the per-distribution "
        f"subclasses, found on the shared base: {sorted(leaked)}"
    )


def test_role_defaults_to_the_shared_message_role_member():
    assert SharedLLMRequest().role is MessageRole.USER


def test_message_role_members_match_the_pre_merge_copy():
    assert {member.value for member in MessageRole} == {
        "system",
        "developer",
        "user",
        "assistant",
        "function",
        "tool",
        "chatbot",
        "model",
    }
