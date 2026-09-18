"""Field-shape regression test for LLMResponse (issue airunner#2188).

Desktop's and services' pre-merge ``LLMResponse`` dataclasses each
carried fields the other side didn't. This pins the full union so a
future edit can't silently drop one side's fields again -- the failure
mode this class of bug takes is a field the code reads via
``getattr``/``chunk.get`` quietly always returning ``None`` instead of
raising, so nothing but a shape test catches it.
"""

from __future__ import annotations

import dataclasses

from airunner_common.llm_response import LLMResponse


# Fields desktop's `src/airunner/components/llm/managers/llm_response.py`
# defined before the merge.
_DESKTOP_FIELDS = {
    "message": "",
    "is_first_message": False,
    "is_end_of_message": False,
    "name": None,
    "node_id": None,
    "sequence_number": 0,
    "request_id": None,
    "tools": None,
    "is_system_message": False,
    "message_type": None,
    "thinking_content": None,
    "tool_name": None,
    "tool_arguments": None,
    "tool_status": None,
    "prompt_tokens": None,
    "completion_tokens": None,
    "total_tokens": None,
}

# Fields services'
# `services/src/airunner_services/llm/llm_response.py` defined before
# the merge.
_SERVICES_FIELDS = {
    "message": "",
    "final_visible_message": None,
    "skip_tts_stream": False,
    "is_first_message": False,
    "is_end_of_message": False,
    "name": None,
    "node_id": None,
    "sequence_number": 0,
    "request_id": None,
    "tools": None,
    "tool_calls": None,
    "is_system_message": False,
    "prompt_tokens": None,
    "completion_tokens": None,
    "total_tokens": None,
    "message_type": None,
    "turn_index": 0,
}


def test_union_contains_every_pre_merge_field_with_its_default():
    response = LLMResponse()
    for name, default in {**_DESKTOP_FIELDS, **_SERVICES_FIELDS}.items():
        assert hasattr(response, name), f"missing field: {name}"
        assert getattr(response, name) == default, (
            f"{name} default changed: expected {default!r}, "
            f"got {getattr(response, name)!r}"
        )


def test_action_defaults_to_shared_chat_enum_member():
    from airunner_common.contract_enums import LLMActionType

    assert LLMResponse().action is LLMActionType.CHAT


def test_field_count_matches_the_union_exactly():
    field_names = {f.name for f in dataclasses.fields(LLMResponse)}
    expected = set(_DESKTOP_FIELDS) | set(_SERVICES_FIELDS) | {"action"}
    assert field_names == expected
