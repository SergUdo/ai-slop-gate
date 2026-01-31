import pytest
from ai_slop_gate.domain.policy import PolicyRule


class TestPolicyRule:
    """Test suite for PolicyRule dataclass."""

    def test_policy_rule_creation(self):
        """Test creating PolicyRule with basic when/then."""
        rule = PolicyRule(
            id="rule-001",
            when={"category": "security"},
            then={"action": "block"}
        )
        
        assert rule.id == "rule-001"
        assert rule.when == {"category": "security"}
        assert rule.then == {"action": "block"}

    def test_policy_rule_complex_when(self):
        """Test PolicyRule with complex when conditions."""
        rule = PolicyRule(
            id="sql-injection-block",
            when={
                "category": "security",
                "signal": "sql_injection",
                "min_confidence": 0.8
            },
            then={"action": "block", "message": "SQL injection detected"}
        )
        
        assert rule.when["category"] == "security"
        assert rule.when["signal"] == "sql_injection"
        assert rule.when["min_confidence"] == 0.8

    def test_policy_rule_complex_then(self):
        """Test PolicyRule with complex then actions."""
        rule = PolicyRule(
            id="rule-001",
            when={"category": "compliance"},
            then={
                "action": "alert",
                "message": "Compliance check failed",
                "severity": "high",
                "notify": ["admin", "security-team"]
            }
        )
        
        assert rule.then["action"] == "alert"
        assert rule.then["notify"] == ["admin", "security-team"]

    def test_policy_rule_immutable(self):
        """Test that PolicyRule is immutable (frozen)."""
        rule = PolicyRule(
            id="rule-001",
            when={"category": "security"},
            then={"action": "block"}
        )
        
        with pytest.raises(AttributeError):
            rule.id = "rule-002"

    def test_policy_rule_when_dict_contents_mutable(self):
        """Test that when dict contents are mutable even in frozen dataclass."""
        rule = PolicyRule(
            id="rule-001",
            when={"category": "security"},
            then={"action": "block"}
        )
        
        # Dicts are mutable, so their contents can be modified
        # even in a frozen dataclass (only the attribute reference is frozen)
        rule.when["category"] = "other"
        assert rule.when["category"] == "other"

    def test_policy_rule_numeric_conditions(self):
        """Test PolicyRule with numeric conditions."""
        rule = PolicyRule(
            id="confidence-rule",
            when={
                "min_confidence": 0.75,
                "max_confidence": 0.95,
                "priority": 10
            },
            then={"action": "review"}
        )
        
        assert rule.when["min_confidence"] == 0.75
        assert rule.when["max_confidence"] == 0.95
        assert rule.when["priority"] == 10

    def test_policy_rule_boolean_conditions(self):
        """Test PolicyRule with boolean conditions."""
        rule = PolicyRule(
            id="bool-rule",
            when={
                "enabled": True,
                "enforced": False
            },
            then={"action": "warn"}
        )
        
        assert rule.when["enabled"] is True
        assert rule.when["enforced"] is False

    def test_policy_rule_nested_structure(self):
        """Test PolicyRule with nested when/then structures."""
        rule = PolicyRule(
            id="nested-rule",
            when={
                "conditions": {
                    "category": "security",
                    "severity": ["high", "critical"]
                }
            },
            then={
                "actions": {
                    "primary": "block",
                    "secondary": "alert"
                }
            }
        )
        
        assert rule.when["conditions"]["category"] == "security"
        assert rule.then["actions"]["primary"] == "block"

    def test_policy_rule_empty_dicts(self):
        """Test PolicyRule with empty when/then."""
        rule = PolicyRule(
            id="empty-rule",
            when={},
            then={}
        )
        
        assert rule.when == {}
        assert rule.then == {}

    def test_policy_rule_list_in_conditions(self):
        """Test PolicyRule with lists in conditions."""
        rule = PolicyRule(
            id="list-rule",
            when={
                "signals": ["sql_injection", "xss", "csrf"],
                "categories": ["security", "compliance"]
            },
            then={
                "actions": ["block", "alert", "log"]
            }
        )
        
        assert len(rule.when["signals"]) == 3
        assert rule.when["signals"][0] == "sql_injection"

    def test_policy_rule_string_id(self):
        """Test PolicyRule with various id formats."""
        ids = [
            "simple",
            "rule-001",
            "my_rule_name",
            "RULE.CATEGORY.SIGNAL",
            "uuid-12345-67890"
        ]
        
        for rule_id in ids:
            rule = PolicyRule(
                id=rule_id,
                when={"test": True},
                then={"action": "test"}
            )
            assert rule.id == rule_id

    def test_policy_rule_null_values_in_conditions(self):
        """Test PolicyRule with null values."""
        rule = PolicyRule(
            id="null-rule",
            when={
                "category": "security",
                "optional_field": None
            },
            then={
                "action": "block",
                "message": None
            }
        )
        
        assert rule.when["optional_field"] is None
        assert rule.then["message"] is None

    def test_policy_rule_complex_real_world_example(self):
        """Test PolicyRule with realistic security rule."""
        rule = PolicyRule(
            id="sql-injection-detection",
            when={
                "category": "security",
                "signal": "sql_injection",
                "min_confidence": 0.8,
                "providers": ["static", "ai-analyzer"]
            },
            then={
                "action": "blocking",
                "message": "SQL injection vulnerability detected",
                "severity": "critical",
                "requires_review": True,
                "notify": ["security@company.com"]
            }
        )
        
        assert rule.id == "sql-injection-detection"
        assert rule.when["signal"] == "sql_injection"
        assert rule.then["action"] == "blocking"
        assert rule.when["min_confidence"] == 0.8

    def test_policy_rule_multiple_instances(self):
        """Test creating multiple PolicyRule instances."""
        rules = [
            PolicyRule(id="rule-1", when={"a": 1}, then={"x": "a"}),
            PolicyRule(id="rule-2", when={"b": 2}, then={"y": "b"}),
            PolicyRule(id="rule-3", when={"c": 3}, then={"z": "c"})
        ]
        
        assert len(rules) == 3
        assert rules[0].id == "rule-1"
        assert rules[1].when["b"] == 2
        assert rules[2].then["z"] == "c"

    def test_policy_rule_unicode_in_conditions(self):
        """Test PolicyRule with unicode characters."""
        rule = PolicyRule(
            id="unicode-rule",
            when={
                "description": "Перевіряє безпеку",
                "language": "укр"
            },
            then={
                "message": "Помилка безпеки!"
            }
        )
        
        assert rule.when["description"] == "Перевіряє безпеку"
        assert rule.then["message"] == "Помилка безпеки!"

    def test_policy_rule_special_characters_in_id(self):
        """Test PolicyRule with special characters in id."""
        rule = PolicyRule(
            id="rule:security/sql-injection#v2.1",
            when={"test": True},
            then={"action": "block"}
        )
        
        assert rule.id == "rule:security/sql-injection#v2.1"
