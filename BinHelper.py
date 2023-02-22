import mmap


def write_bytes_at_offset(mm: mmap, offset: int, value: bytearray):
    length = len(value)
    mm[offset:offset+length] = value


def flip_error_bytes(error: str) -> str:
    split = [error[i:i+2] for i in range(0, len(error), 2)]
    split.reverse()
    result = ""
    result = result.join(split)
    return result


def precision_search(key: bytearray, array: mmap, allowed_error: float) -> int:
    for i in range(0, len(array) - len(key) + 1):
        unequal_counter = 0
        found = True

        for j in range(0, len(key)):
            if array[i + j] != key[j]:
                unequal_counter += 1

            if unequal_counter / len(key) > allowed_error:
                found = False
                break

        if found:
            return i

    return -1
