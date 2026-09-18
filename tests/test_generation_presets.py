"""Regression pins for the shared action-preset table (#2225).

This is the single source of truth desktop's and services'
``LLMRequest.for_action()`` both call now. The pins here are deliberately
explicit (exact temperatures, exact tool-category shapes) rather than
"agrees with itself", because the whole point of #2225 is that an
*undocumented* drift is what caused the fork in the first place.
"""

from __future__ import annotations

from airunner_common.contract_enums import LLMActionType
from airunner_common.generation_presets import (
    ACTION_GENERATION_PRESETS,
    DEFAULT_ACTION_PRESET,
    GenerationPreset,
    get_action_generation_preset,
)

# The actions no table maps explicitly; both sides must fall back to the
# same default preset. The default means "all tools" (tool_categories is
# None), which is the desktop behavior #2225 adopted. GENERATE_IMAGE is
# *not* here -- it is an explicit entry (temperature 0.9) that simply
# inherits the same None (all tools) default.
_UNMAPPED_ACTIONS = (
    LLMActionType.NONE,
    LLMActionType.QUIT_APPLICATION,
    LLMActionType.TOGGLE_FULLSCREEN,
    LLMActionType.TOGGLE_TTS,
    LLMActionType.DO_NOTHING,
    LLMActionType.GET_WEATHER,
    LLMActionType.STORE_DATA,
)


def test_every_action_resolves_to_a_preset():
    for action in LLMActionType:
        preset = get_action_generation_preset(action)
        assert isinstance(preset, GenerationPreset)


def test_chat_and_mood_use_the_documented_low_variance_temperature():
    """The 0.2 chat temperature is the deliberately-tuned desktop value."""
    assert ACTION_GENERATION_PRESETS[LLMActionType.CHAT].temperature == 0.2
    assert ACTION_GENERATION_PRESETS[LLMActionType.UPDATE_MOOD].temperature == 0.2


def test_rag_and_search_use_the_documented_deterministic_temperature():
    for action in (
        LLMActionType.PERFORM_RAG_SEARCH,
        LLMActionType.SUMMARIZE,
        LLMActionType.SEARCH,
    ):
        assert ACTION_GENERATION_PRESETS[action].temperature == 0.2


def test_the_stale_services_temperatures_are_gone():
    """Pin the *unified* values, not the forked services ones (#2225).

    The services fork used 0.7 for chat and 0.3 for RAG/search; neither
    may reappear in the single source of truth without this failing.
    """
    assert ACTION_GENERATION_PRESETS[LLMActionType.CHAT].temperature != 0.7
    assert (
        ACTION_GENERATION_PRESETS[LLMActionType.PERFORM_RAG_SEARCH].temperature != 0.3
    )


def test_unmapped_actions_mean_all_tools_not_no_tools():
    """Unmapped actions resolve to ``None`` (all tools), never ``[]``."""
    for action in _UNMAPPED_ACTIONS:
        preset = get_action_generation_preset(action)
        assert preset is DEFAULT_ACTION_PRESET
        assert preset.tool_categories is None
        assert preset.to_request_kwargs()["tool_categories"] is None


def test_image_generation_keeps_its_temperature_but_means_all_tools():
    """GENERATE_IMAGE is mapped for temperature, defaulted for tools."""
    preset = ACTION_GENERATION_PRESETS[LLMActionType.GENERATE_IMAGE]
    assert preset.temperature == 0.9
    assert preset.to_request_kwargs()["tool_categories"] is None


def test_tool_categories_tuple_becomes_a_list_and_none_stays_none():
    assert ACTION_GENERATION_PRESETS[LLMActionType.DEEP_RESEARCH].to_request_kwargs()[
        "tool_categories"
    ] == ["RESEARCH", "SEARCH"]
    assert (
        ACTION_GENERATION_PRESETS[LLMActionType.CHAT].to_request_kwargs()[
            "tool_categories"
        ]
        is None
    )


def test_to_request_kwargs_covers_every_preset_field():
    kwargs = ACTION_GENERATION_PRESETS[LLMActionType.CHAT].to_request_kwargs()
    assert set(kwargs) == {
        f.name for f in GenerationPreset.__dataclass_fields__.values()
    }
