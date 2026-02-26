"""
BitHide Backend - Custom Exception Hierarchy
Centralized exception definitions for all layers.
"""


class BitHideException(Exception):
    """Base exception for the BitHide application."""

    def __init__(self, message: str = "An internal error occurred.", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self) -> dict:
        return {"error": True, "message": self.message, "status": self.status_code}


# ─── File Validation ─────────────────────────────────────────────────────────

class InvalidFileTypeError(BitHideException):
    def __init__(self, mime_type: str = ""):
        super().__init__(
            message=f"Unsupported file type: '{mime_type}'. Allowed: JPEG, PNG, MP3, WAV, PDF.",
            status_code=415,
        )


class FileTooLargeError(BitHideException):
    def __init__(self, max_mb: int = 50):
        super().__init__(
            message=f"File exceeds the maximum allowed size of {max_mb} MB.",
            status_code=413,
        )


class MissingFileError(BitHideException):
    def __init__(self):
        super().__init__(message="No file was provided in the request.", status_code=400)


# ─── Input Validation ─────────────────────────────────────────────────────────

class MessageTooLongError(BitHideException):
    def __init__(self, max_len: int = 5000):
        super().__init__(
            message=f"Message exceeds maximum length of {max_len} characters.",
            status_code=422,
        )


class WeakKeyError(BitHideException):
    def __init__(self, min_len: int = 8):
        super().__init__(
            message=f"Passphrase must be at least {min_len} characters long.",
            status_code=422,
        )


class MissingFieldError(BitHideException):
    def __init__(self, field: str):
        super().__init__(message=f"Required field missing: '{field}'.", status_code=400)


# ─── Encryption / Decryption ─────────────────────────────────────────────────

class EncryptionError(BitHideException):
    def __init__(self, detail: str = ""):
        super().__init__(
            message=f"Encryption failed. {detail}".strip(),
            status_code=500,
        )


class DecryptionError(BitHideException):
    def __init__(self):
        super().__init__(
            message="Decryption failed. The passphrase is incorrect or the file has been tampered with.",
            status_code=422,
        )


# ─── Steganography ───────────────────────────────────────────────────────────

class PayloadTooLargeForCarrierError(BitHideException):
    def __init__(self):
        super().__init__(
            message="The encrypted message is too large to embed into the provided carrier file.",
            status_code=422,
        )


class ExtractionError(BitHideException):
    def __init__(self, detail: str = ""):
        super().__init__(
            message=f"Failed to extract hidden data from file. {detail}".strip(),
            status_code=422,
        )


# ─── Processing ──────────────────────────────────────────────────────────────

class UnsupportedOperationError(BitHideException):
    def __init__(self, detail: str = ""):
        super().__init__(
            message=f"Unsupported operation for this file type. {detail}".strip(),
            status_code=400,
        )
