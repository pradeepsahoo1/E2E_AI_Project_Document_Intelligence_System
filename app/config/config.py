"""Typed configuration with hosted model providers."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_env: str = "development"
    auth_mode: str = "sqlite"
    jwt_secret: str = ""
    jwt_issuer: str = "enterprise-document-intelligence-system"
    jwt_audience: str = "edis-api"
    storage_dir: Path | None = None
    dataset_dir: Path = Path(__file__).resolve().parents[2] / "documents"
    output_dir: Path = Path(__file__).resolve().parents[2] / "output"
    llm_provider: str = "groq"
    embedding_provider: str = "huggingface"
    vector_backend: str = "chroma"
    google_api_key: str = ""
    groq_api_key: str = ""
    huggingface_token: str = field(default="", repr=False)
    google_chat_model: str = "gemini-3.5-flash"
    groq_chat_model: str = "qwen/qwen3.8-27b"
    groq_fallback_models: tuple[str, ...] = ("openai/gpt-oss-120b", "openai/gpt-oss-20b")
    google_embedding_model: str = "models/gemini-embedding-001"
    huggingface_embedding_model: str = "BAAI/bge-small-en-v1.5"
    max_upload_mb: int = 15
    max_pages: int = 100
    max_extracted_chars: int = 500_000
    max_analysis_file_mb: int = 50
    max_analysis_pages: int = 1000
    max_analysis_extracted_chars: int = 5_000_000
    max_files_per_request: int = 5
    max_dataset_files: int = 100
    max_dataset_file_mb: int = 50
    max_dataset_pages: int = 1000
    max_dataset_extracted_chars: int = 5_000_000
    chunk_size: int = 1600
    chunk_overlap: int = 100
    cors_origins: tuple[str, ...] = ("http://localhost:8080", "http://127.0.0.1:8080")

    @property
    def storage_root(self) -> Path:
        return self.storage_dir if self.storage_dir is not None else self.output_dir / "storage"

    @classmethod
    def from_env(cls) -> "Settings":
        storage_dir = os.getenv("STORAGE_DIR")
        google_api_key = os.getenv("GOOGLE_API_KEY", "")
        groq_api_key = os.getenv("GROQ_API_KEY", "")
        huggingface_token = (
            os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACEHUB_API_TOKEN") or ""
        ).strip()
        default_llm = "groq" if groq_api_key else "google" if google_api_key else cls.llm_provider
        # The fields above are the defaults. Deployments can override them.
        return cls(
            app_env=os.getenv("APP_ENV", cls.app_env).lower(),
            auth_mode=os.getenv("AUTH_MODE", cls.auth_mode).lower(),
            jwt_secret=os.getenv("JWT_SECRET", ""),
            jwt_issuer=os.getenv("JWT_ISSUER", cls.jwt_issuer),
            jwt_audience=os.getenv("JWT_AUDIENCE", cls.jwt_audience),
            storage_dir=Path(storage_dir).resolve() if storage_dir else cls.storage_dir,
            dataset_dir=Path(os.getenv("DATASET_DIR", str(cls.dataset_dir))).resolve(),
            output_dir=Path(os.getenv("OUTPUT_DIR", str(cls.output_dir))).resolve(),
            llm_provider=os.getenv("LLM_PROVIDER", default_llm).lower(),
            embedding_provider=os.getenv("EMBEDDING_PROVIDER", cls.embedding_provider).lower(),
            vector_backend=os.getenv("VECTOR_BACKEND", cls.vector_backend).lower(),
            google_api_key=google_api_key,
            groq_api_key=groq_api_key,
            huggingface_token=huggingface_token,
            google_chat_model=os.getenv("GOOGLE_CHAT_MODEL", cls.google_chat_model),
            groq_chat_model=os.getenv("GROQ_CHAT_MODEL", cls.groq_chat_model),
            google_embedding_model=os.getenv("GOOGLE_EMBEDDING_MODEL", cls.google_embedding_model),
            huggingface_embedding_model=os.getenv(
                "HUGGINGFACE_EMBEDDING_MODEL", cls.huggingface_embedding_model
            ),
            max_upload_mb=int(os.getenv("MAX_UPLOAD_MB", str(cls.max_upload_mb))),
            max_pages=int(os.getenv("MAX_PAGES", str(cls.max_pages))),
            max_extracted_chars=int(os.getenv("MAX_EXTRACTED_CHARS", str(cls.max_extracted_chars))),
            max_analysis_file_mb=int(os.getenv("MAX_ANALYSIS_FILE_MB", str(cls.max_analysis_file_mb))),
            max_analysis_pages=int(os.getenv("MAX_ANALYSIS_PAGES", str(cls.max_analysis_pages))),
            max_analysis_extracted_chars=int(
                os.getenv("MAX_ANALYSIS_EXTRACTED_CHARS", str(cls.max_analysis_extracted_chars))
            ),
            max_files_per_request=int(os.getenv("MAX_FILES_PER_REQUEST", str(cls.max_files_per_request))),
            max_dataset_files=int(os.getenv("MAX_DATASET_FILES", str(cls.max_dataset_files))),
            max_dataset_file_mb=int(os.getenv("MAX_DATASET_FILE_MB", str(cls.max_dataset_file_mb))),
            max_dataset_pages=int(os.getenv("MAX_DATASET_PAGES", str(cls.max_dataset_pages))),
            max_dataset_extracted_chars=int(
                os.getenv("MAX_DATASET_EXTRACTED_CHARS", str(cls.max_dataset_extracted_chars))
            ),
            chunk_size=int(os.getenv("CHUNK_SIZE", str(cls.chunk_size))),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", str(cls.chunk_overlap))),
            cors_origins=tuple(
                origin.strip()
                for origin in os.getenv("CORS_ORIGINS", ",".join(cls.cors_origins)).split(",")
                if origin.strip()
            ),
        ).validate()

    def validate(self) -> "Settings":
        if self.app_env not in ("development", "test", "production"):
            raise ValueError("APP_ENV must be development, test or production")
        if self.auth_mode not in ("sqlite", "local", "jwt"):
            raise ValueError("AUTH_MODE must be sqlite, local or jwt")
        if self.app_env == "production" and self.auth_mode != "jwt":
            raise ValueError("Production requires AUTH_MODE=jwt")
        if self.auth_mode == "jwt" and len(self.jwt_secret) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters in jwt mode")
        if self.llm_provider not in ("google", "groq"):
            raise ValueError("LLM_PROVIDER must be google or groq")
        if self.embedding_provider not in ("google", "huggingface"):
            raise ValueError("EMBEDDING_PROVIDER must be google or huggingface")
        if self.vector_backend != "chroma":
            raise ValueError("VECTOR_BACKEND must be chroma")
        if self.llm_provider == "google" or self.embedding_provider == "google":
            if not self.google_api_key:
                raise ValueError("GOOGLE_API_KEY required for google models")
        if self.llm_provider == "groq" and not self.groq_api_key:
            raise ValueError("GROQ_API_KEY required for Groq model")
        # Hugging Face token validation is currently commented out
        ##if self.embedding_provider == "huggingface" and not self.huggingface_token:
        ##    raise ValueError("HF_TOKEN or HUGGINGFACEHUB_API_TOKEN required for Hugging Face inference")
        limits = (
            self.max_upload_mb,
            self.max_pages,
            self.max_extracted_chars,
            self.max_analysis_file_mb,
            self.max_analysis_pages,
            self.max_analysis_extracted_chars,
            self.max_files_per_request,
            self.max_dataset_files,
            self.max_dataset_file_mb,
            self.max_dataset_pages,
            self.max_dataset_extracted_chars,
        )
        if any(value < 1 for value in limits):
            raise ValueError("Upload limits must be positive")
        if not 1 <= self.chunk_overlap < self.chunk_size:
            raise ValueError("CHUNK_OVERLAP must be >= 1 and < CHUNK_SIZE")
        if "*" in self.cors_origins:
            raise ValueError("Wildcard CORS is disabled; configure allowed origins explicitly")
        return self
