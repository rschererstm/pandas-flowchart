"""
Tests for the FlowTracker class and pandas interceptors.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas_flow
from pandas_flow.events import OperationType
from pandas_flow.tracker import FlowTracker


class TestFlowTrackerSetup:
    """Tests for FlowTracker initialization and setup."""

    def test_basic_setup(self):
        """Test basic tracker setup."""
        flow = pandas_flow.setup(auto_intercept=False)

        assert isinstance(flow, FlowTracker)
        assert flow.track_row_count is True
        assert len(flow.events) == 0

    def test_setup_with_variables(self):
        """Test setup with tracked variables."""
        flow = pandas_flow.setup(
            track_variables={
                "col_a": "n_unique",
                "col_b": "n_non_null",
            },
            stats_variable="col_c",
            auto_intercept=False,
        )

        assert flow.track_variables == {"col_a": "n_unique", "col_b": "n_non_null"}
        assert flow.stats_variable == "col_c"

    def test_setup_with_theme(self):
        """Test setup with different themes."""
        for theme in ["default", "dark", "light"]:
            flow = pandas_flow.setup(theme=theme, auto_intercept=False)
            assert flow.theme == theme


class TestEventRecording:
    """Tests for event recording functionality."""

    def setup_method(self):
        """Setup for each test."""
        self.flow = FlowTracker()

    def test_record_single_operation(self):
        """Test recording a single operation."""
        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})

        self.flow.record_operation(
            operation_type=OperationType.FILTER,
            operation_name="Test Filter",
            input_dfs=[df],
            output_df=df[df["a"] > 1],
            description="Filter rows where a > 1",
        )

        assert len(self.flow.events) == 1
        event = self.flow.events[0]
        assert event.operation_type == OperationType.FILTER
        assert event.operation_name == "Test Filter"
        assert event.output_df.n_rows == 2

    def test_record_merge_operation(self):
        """Test recording a merge operation."""
        df1 = pd.DataFrame({"key": [1, 2], "value1": ["a", "b"]})
        df2 = pd.DataFrame({"key": [1, 2], "value2": ["x", "y"]})
        merged = df1.merge(df2, on="key")

        self.flow.record_operation(
            operation_type=OperationType.MERGE,
            operation_name="Test Merge",
            input_dfs=[df1, df2],
            output_df=merged,
            description="Inner join on key",
        )

        assert len(self.flow.events) == 1
        event = self.flow.events[0]
        assert len(event.input_dfs) == 2
        assert event.output_df.n_cols == 3

    def test_event_ids_are_unique(self):
        """Test that event IDs are unique."""
        df = pd.DataFrame({"a": [1, 2, 3]})

        for i in range(5):
            self.flow.record_operation(
                operation_type=OperationType.CUSTOM,
                operation_name=f"Op {i}",
                input_dfs=[df],
                output_df=df,
            )

        event_ids = [e.event_id for e in self.flow.events]
        assert len(event_ids) == len(set(event_ids))


class TestStatisticsCalculation:
    """Tests for statistics calculation."""

    def setup_method(self):
        """Setup for each test."""
        self.flow = FlowTracker(
            track_variables={"id": "n_unique", "category": "n_unique"},
            stats_variable="value",
            stats_types=["min", "max", "mean", "std", "histogram"],
        )

    def test_tracked_variable_stats(self):
        """Test that tracked variables are computed."""
        df = pd.DataFrame(
            {
                "id": [1, 2, 3, 3, 4],
                "category": ["A", "B", "A", "C", "B"],
                "value": [10, 20, 30, 40, 50],
            }
        )

        self.flow.record_operation(
            operation_type=OperationType.CUSTOM,
            operation_name="Test",
            input_dfs=[df],
            output_df=df,
        )

        event = self.flow.events[0]
        stats_names = [s.name for s in event.tracked_stats]

        assert "id" in stats_names
        assert "category" in stats_names
        assert "value" in stats_names

    def test_stats_variable_detailed_stats(self):
        """Test detailed stats for stats_variable."""
        np.random.seed(42)
        df = pd.DataFrame(
            {
                "id": range(100),
                "value": np.random.normal(50, 10, 100),
            }
        )

        self.flow.record_operation(
            operation_type=OperationType.CUSTOM,
            operation_name="Test",
            input_dfs=[df],
            output_df=df,
        )

        event = self.flow.events[0]
        value_stats = next(s for s in event.tracked_stats if s.name == "value")

        assert value_stats.min_value is not None
        assert value_stats.max_value is not None
        assert value_stats.mean_value is not None
        assert value_stats.std_value is not None
        assert len(value_stats.histogram) > 0


class TestMermaidRendering:
    """Tests for Mermaid diagram generation."""

    def setup_method(self):
        """Setup for each test."""
        self.flow = FlowTracker()

    def test_empty_diagram(self):
        """Test rendering with no events."""
        mermaid = self.flow.get_mermaid()

        assert "flowchart" in mermaid
        assert "No operations recorded" in mermaid

    def test_basic_diagram(self):
        """Test rendering a basic diagram."""
        df = pd.DataFrame({"a": [1, 2, 3]})

        self.flow.record_operation(
            operation_type=OperationType.READ_CSV,
            operation_name="Load Data",
            input_dfs=[],
            output_df=df,
            description="Load from file",
        )

        self.flow.record_operation(
            operation_type=OperationType.FILTER,
            operation_name="Filter",
            input_dfs=[df],
            output_df=df[df["a"] > 1],
        )

        mermaid = self.flow.get_mermaid()

        assert "flowchart" in mermaid
        assert "Load Data" in mermaid
        assert "Filter" in mermaid
        assert "-->" in mermaid or "==>" in mermaid or "-.->" in mermaid

    def test_diagram_with_styles(self):
        """Test that styles are generated."""
        df = pd.DataFrame({"a": [1, 2, 3]})

        self.flow.record_operation(
            operation_type=OperationType.FILTER,
            operation_name="Filter",
            input_dfs=[df],
            output_df=df,
        )

        mermaid = self.flow.get_mermaid()

        assert "style" in mermaid
        assert "fill:" in mermaid


class TestInterceptors:
    """Tests for pandas operation interception."""

    def setup_method(self):
        """Setup for each test with interceptors enabled."""
        self.flow = pandas_flow.setup(auto_intercept=True)

    def teardown_method(self):
        """Cleanup after each test."""
        if hasattr(self, "flow"):
            self.flow.uninstall_interceptors()
            self.flow.clear()

    def test_intercept_merge(self):
        """Test that merge is intercepted."""
        self.flow.clear()

        df1 = pd.DataFrame({"key": [1, 2], "val1": ["a", "b"]})
        df2 = pd.DataFrame({"key": [1, 2], "val2": ["x", "y"]})

        _result = df1.merge(df2, on="key")  # noqa: F841

        # Find merge event
        merge_events = [e for e in self.flow.events if e.operation_type == OperationType.MERGE]
        assert len(merge_events) >= 1

    def test_intercept_query(self):
        """Test that query is intercepted."""
        self.flow.clear()

        df = pd.DataFrame({"a": [1, 2, 3, 4, 5], "b": ["x", "y", "x", "y", "x"]})
        _result = df.query("a > 2")  # noqa: F841

        query_events = [e for e in self.flow.events if e.operation_type == OperationType.QUERY]
        assert len(query_events) >= 1

    def test_intercept_assign(self):
        """Test that assign is intercepted."""
        self.flow.clear()

        df = pd.DataFrame({"a": [1, 2, 3]})
        _result = df.assign(b=lambda x: x["a"] * 2)  # noqa: F841

        assign_events = [e for e in self.flow.events if e.operation_type == OperationType.ASSIGN]
        assert len(assign_events) >= 1

    def test_intercept_drop(self):
        """Test that drop is intercepted."""
        self.flow.clear()

        df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
        _result = df.drop(columns=["b"])  # noqa: F841

        drop_events = [e for e in self.flow.events if e.operation_type == OperationType.DROP]
        assert len(drop_events) >= 1


class TestOutputFormats:
    """Tests for output format generation."""

    def setup_method(self):
        """Setup for each test."""
        self.flow = FlowTracker()
        df = pd.DataFrame({"a": [1, 2, 3]})

        self.flow.record_operation(
            operation_type=OperationType.CUSTOM,
            operation_name="Test Op",
            input_dfs=[df],
            output_df=df,
        )

    def test_markdown_output(self, tmp_path):
        """Test Markdown output."""
        output_file = tmp_path / "test.md"
        self.flow.render(str(output_file), title="Test")

        content = output_file.read_text()
        assert "# Test" in content
        assert "```mermaid" in content

    def test_html_output(self, tmp_path):
        """Test HTML output."""
        output_file = tmp_path / "test.html"
        self.flow.render(str(output_file), title="Test")

        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "mermaid" in content.lower()

    def test_mermaid_output(self, tmp_path):
        """Test raw Mermaid output."""
        output_file = tmp_path / "test.mmd"
        self.flow.render(str(output_file), title="Test")

        content = output_file.read_text()
        assert "flowchart" in content
        assert "<!DOCTYPE" not in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
