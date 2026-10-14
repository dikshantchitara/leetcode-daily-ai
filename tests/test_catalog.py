from daily_solver.catalog import load_catalog, load_completed


def test_catalog_contains_valid_reviewed_entries():
    entries = load_catalog("catalog/problems.json")
    assert len(entries) >= 2
    assert all(problem.source == "catalog" for problem, _ in entries)
    assert all(solution.implementation for _, solution in entries)


def test_completed_urls_are_normalized(tmp_path):
    completed = tmp_path / "completed.json"
    completed.write_text('["https://leetcode.com/problems/two-sum/"]', encoding="utf-8")
    assert load_completed(str(completed)) == {"https://leetcode.com/problems/two-sum"}
