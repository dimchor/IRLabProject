class Boolean:
    def operator_or(lhs: set[int], rhs: set[int]) -> set[int]:
        return lhs.union(rhs)

    def operator_and(lhs: set[int], rhs: set[int]) -> set[int]:
        return lhs.intersection(rhs)
