from pathlib import Path


def test_pypi_publish_is_manual_and_disabled_by_default() -> None:
    workflow = (
        Path(__file__).parents[1] / ".github/workflows/publish.yml"
    ).read_text(encoding="utf-8")

    events = workflow.split("jobs:", 1)[0]
    assert "  release:" not in events
    assert "  workflow_dispatch:\n    inputs:\n      publish_pypi:" in events
    assert "        type: boolean\n        default: false" in events

    job = workflow.split("  build-and-publish:", 1)[1]
    assert (
        "if: github.event_name == 'workflow_dispatch' "
        "&& inputs.publish_pypi == true"
    ) in job
    assert "    permissions:\n      contents: read\n" in job
    assert "      id-token: write" in job
    assert "  id-token: write" not in events
