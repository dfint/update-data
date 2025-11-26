from typing import Iterable, Iterator, NamedTuple, Optional

import alternative_encodings

alternative_encodings.register_all()


def get_letters(encoding: str, min_code: int=0) -> Iterator[str]:
    for i in range(min_code, 256):
        try:
            char = bytes([i]).decode(encoding)
            if char.isalpha():
                yield char
        except UnicodeDecodeError:
            pass


def get_capitalize_map(letters: Iterable[str]) -> Iterator[tuple[str, str]]:
    for letter in letters:
        cap = letter.capitalize()
        if cap != letter and cap in letters:
            yield letter, cap


def get_lower_map(letters: Iterable[str]) -> Iterator[tuple[str, str]]:
    for letter in letters:
        low = letter.lower()
        if low != letter and low in letters:
            yield letter, low


class State(NamedTuple):
    from_code: int
    to_code: int
    from_letter: str
    to_letter: str
    
    @property
    def diff(self):
        return self.to_code - self.from_code
    
    def is_plus_one(self, other):
        return abs(other.from_code - self.from_code) <= 1 and abs(other.to_code - self.to_code) <= 1


def format_result(state_start: State, state_end: State) -> str:
    if state_end == state_start:
        return f"{state_end.from_code} = {state_start.diff} # {state_end.from_letter} -> {state_end.to_letter}"
    else:
        return (
            f"\"{state_start.from_code}:{state_end.from_code}\" = {state_start.diff} "
            f"# {state_start.from_letter}-{state_end.from_letter} -> {state_start.to_letter}-{state_end.to_letter}"
        )


def group_mapping(mapping: Iterable[tuple[str, str]], encoding: str) -> Iterator[str]:
    state_start: Optional[State] = None
    prev_state: Optional[State] = None
    
    for from_letter, to_letter in mapping:
        current_state = State(
            from_code=from_letter.encode(encoding)[0],
            to_code=to_letter.encode(encoding)[0],
            from_letter=from_letter,
            to_letter=to_letter,
        )
        
        if state_start is None:
            state_start = current_state
            prev_state = current_state

        if not current_state.is_plus_one(prev_state):
            yield format_result(state_start, prev_state)
            state_start = current_state
        
        prev_state = current_state
    
    if prev_state:
        yield format_result(state_start, prev_state)


def main(encoding: str):
    print("[metadata]")
    print(f"encoding = \"{encoding}\"")
    print()
    
    letters = list(get_letters(encoding))
    
    print("[maps.capitalize]")
    capitalize_map = list(get_capitalize_map(letters))
    for line in group_mapping(capitalize_map, encoding):
        print(line)
    
    print()
    
    print("[maps.lowercast]")
    lower_map = list(get_lower_map(letters))
    for line in group_mapping(lower_map, encoding):
        print(line)

    print()
    
    print("[maps.utf]")
    letters = get_letters(encoding, 128)
    for letter in letters:
        code = letter.encode(encoding)[0]
        utf8_code = int.from_bytes(letter.encode("utf-8"), byteorder="little")
        print(f"{utf8_code} = {code} # {letter}")

    print()

    print("[maps.uppercase]")
    print()

    print("[maps.lowercase]")
    print()

    print("[maps.simplify]")
    print()

if __name__ == "__main__":
    import sys
    main(sys.argv[1])
