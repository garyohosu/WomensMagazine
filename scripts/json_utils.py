import json
from typing import Type, TypeVar

T = TypeVar("T")


def extract_json_value(raw: str, expected_type: Type[T]) -> T:
    """
    Extract the first valid JSON value of expected_type from text.
    Handles model responses that contain extra prose before/after JSON.
    """
    raw = raw.strip()
    decoder = json.JSONDecoder()

    # Fast path: the whole response is clean JSON.
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, expected_type):
            return parsed
    except json.JSONDecodeError:
        pass

    for idx, ch in enumerate(raw):
        if ch not in "{[":
            continue
        try:
            parsed, _ = decoder.raw_decode(raw[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, expected_type):
            return parsed

    raise ValueError(f"Expected JSON {expected_type.__name__} was not found in model output.")
