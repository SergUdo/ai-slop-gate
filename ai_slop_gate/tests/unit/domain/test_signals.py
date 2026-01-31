import pytest
from ai_slop_gate.domain.signals import Signal


class TestSignal:
    """Test suite for Signal enum."""

    def test_signal_insecure_config(self):
        """Test INSECURE_CONFIG signal value."""
        assert Signal.INSECURE_CONFIG == "insecure_config"

    def test_signal_best_practice(self):
        """Test BEST_PRACTICE signal value."""
        assert Signal.BEST_PRACTICE == "best_practice"

    def test_signal_misconfiguration(self):
        """Test MISCONFIGURATION signal value."""
        assert Signal.MISCONFIGURATION == "misconfiguration"

    def test_signal_string_comparison(self):
        """Test comparing signal with string."""
        sig = Signal.INSECURE_CONFIG
        assert sig == "insecure_config"

    def test_signal_is_enum(self):
        """Test that Signal is an enum."""
        assert isinstance(Signal.INSECURE_CONFIG, Signal)
        assert isinstance(Signal.BEST_PRACTICE, Signal)
        assert isinstance(Signal.MISCONFIGURATION, Signal)

    def test_signal_in_list(self):
        """Test checking if signal is in list."""
        signals = [Signal.INSECURE_CONFIG, Signal.BEST_PRACTICE]
        
        assert Signal.INSECURE_CONFIG in signals
        assert Signal.BEST_PRACTICE in signals
        assert Signal.MISCONFIGURATION not in signals

    def test_signal_value_access(self):
        """Test accessing signal value."""
        sig = Signal.INSECURE_CONFIG
        assert sig.value == "insecure_config"

    def test_signal_name_access(self):
        """Test accessing signal name."""
        sig = Signal.INSECURE_CONFIG
        assert sig.name == "INSECURE_CONFIG"

    def test_all_signals_enumerable(self):
        """Test that all signals can be enumerated."""
        signal_values = [s.value for s in Signal]
        
        assert "insecure_config" in signal_values
        assert "best_practice" in signal_values
        assert "misconfiguration" in signal_values
        assert len(signal_values) == 3

    def test_signal_equality(self):
        """Test signal equality comparisons."""
        sig1 = Signal.INSECURE_CONFIG
        sig2 = Signal.INSECURE_CONFIG
        sig3 = Signal.BEST_PRACTICE
        
        assert sig1 == sig2
        assert sig1 != sig3

    def test_signal_from_string(self):
        """Test creating Signal from string value."""
        sig = Signal("insecure_config")
        assert sig == Signal.INSECURE_CONFIG

    def test_signal_from_name(self):
        """Test creating Signal from name."""
        sig = Signal["INSECURE_CONFIG"]
        assert sig == Signal.INSECURE_CONFIG

    def test_signal_iteration(self):
        """Test iterating over all signals."""
        signals = list(Signal)
        
        assert len(signals) == 3
        assert Signal.INSECURE_CONFIG in signals
        assert Signal.BEST_PRACTICE in signals
        assert Signal.MISCONFIGURATION in signals

    def test_signal_in_dictionary(self):
        """Test using Signal as dictionary key."""
        signal_map = {
            Signal.INSECURE_CONFIG: "insecure",
            Signal.BEST_PRACTICE: "best",
            Signal.MISCONFIGURATION: "misc"
        }
        
        assert signal_map[Signal.INSECURE_CONFIG] == "insecure"
        assert signal_map[Signal.BEST_PRACTICE] == "best"

    def test_signal_in_set(self):
        """Test using Signal in sets."""
        signal_set = {Signal.INSECURE_CONFIG, Signal.BEST_PRACTICE}
        
        assert Signal.INSECURE_CONFIG in signal_set
        assert Signal.BEST_PRACTICE in signal_set
        assert Signal.MISCONFIGURATION not in signal_set

    def test_signal_string_conversion(self):
        """Test converting Signal to string."""
        sig = Signal.INSECURE_CONFIG
        assert str(sig) == "Signal.INSECURE_CONFIG"

    def test_signal_comparison_with_value_string(self):
        """Test that Signal equals its string value."""
        sig = Signal.BEST_PRACTICE
        value_str = "best_practice"
        
        assert sig == value_str
        # String comparison works both ways since Signal extends str
        assert value_str == sig

    def test_signal_hashable(self):
        """Test that Signal instances are hashable."""
        sig1 = Signal.INSECURE_CONFIG
        sig2 = Signal.INSECURE_CONFIG
        
        # Can use as dict keys
        d = {sig1: "value"}
        assert d[sig2] == "value"
