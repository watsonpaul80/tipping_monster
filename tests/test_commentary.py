from utils.commentary import generate_commentary


def test_generate_commentary_basic():
    tags = ["⚡ Fresh", "🔽 Class Drop", "🔥 Trainer 72%"]
    result = generate_commentary(tags, 0.92)
    assert result == "✍️ Fresh off a break | Class drop | Trainer in form (RTF 72%)"


def test_generate_commentary_empty():
    assert (
        generate_commentary([], 0.5) == "✍️ No standout signals — check form manually."
    )
