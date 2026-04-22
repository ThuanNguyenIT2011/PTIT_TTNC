class SearchResult:
    def __init__(self, positions=None, comparisons=0, elapsed_ms=0.0):
        self.positions = positions or []
        self.comparisons = comparisons
        self.elapsed_ms = elapsed_ms