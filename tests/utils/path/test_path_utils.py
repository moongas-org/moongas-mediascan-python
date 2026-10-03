from mediascan.utils.path import get_human_readable_size

def test_get_human_readable_size():
    assert get_human_readable_size(0) == "0.00 B"
    assert get_human_readable_size(1023) == "1023.00 B"
    assert get_human_readable_size(1024) == "1.00 KB"
    assert get_human_readable_size(1024**2-1024**1) == "1023.00 KB"
    assert get_human_readable_size(1024**2) == "1.00 MB"
    assert get_human_readable_size(1024**3-1024**2) == "1023.00 MB"
    assert get_human_readable_size(1024**3) == "1.00 GB"
    assert get_human_readable_size(1024**4-1024**3) == "1023.00 GB"
    assert get_human_readable_size(1024**4) == "1.00 TB"
    assert get_human_readable_size(1024**5-1024**4) == "1023.00 TB"
    assert get_human_readable_size(1024**5) == "1.00 PB"
    assert get_human_readable_size(1024**6-1024**5) == "1023.00 PB"
    assert get_human_readable_size(1024**6) == "1024.00 PB"
