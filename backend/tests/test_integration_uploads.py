import base64
import io

# A real, minimal 1x1 PNG -- valid enough to exercise the actual upload
# path, not just a content-type label.
TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def test_logged_out_blocked(client):
    res = client.post(
        "/uploads/image", files={"file": ("test.png", io.BytesIO(TINY_PNG), "image/png")}
    )
    assert res.status_code == 401


def test_upload_returns_usable_data_uri(student_client):
    res = student_client.post(
        "/uploads/image", files={"file": ("test.png", io.BytesIO(TINY_PNG), "image/png")}
    )
    assert res.status_code == 200
    url = res.json()["url"]
    assert url.startswith("data:image/png;base64,")
    # round-trips back to the exact original bytes
    _, encoded = url.split(",", 1)
    assert base64.b64decode(encoded) == TINY_PNG


def test_wrong_content_type_rejected(student_client):
    res = student_client.post(
        "/uploads/image",
        files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
    )
    assert res.status_code == 400


def test_oversized_file_rejected(student_client):
    big = b"\x00" * (2 * 1024 * 1024 + 1)
    res = student_client.post(
        "/uploads/image", files={"file": ("big.png", io.BytesIO(big), "image/png")}
    )
    assert res.status_code == 400


def test_empty_file_rejected(student_client):
    res = student_client.post(
        "/uploads/image", files={"file": ("empty.png", io.BytesIO(b""), "image/png")}
    )
    assert res.status_code == 400
