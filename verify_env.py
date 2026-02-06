"""
Quick script to verify .env configuration is loaded correctly.
Run this before starting the server to ensure API keys are properly configured.
"""

from app.core.config import get_settings

def verify_env():
    """Verify environment configuration."""
    print("=" * 60)
    print("Environment Configuration Verification")
    print("=" * 60)

    settings = get_settings()

    # Check OpenAI API Key
    print("\n1. OpenAI Configuration:")
    if settings.openai_api_key:
        # Don't print the full key for security
        key_preview = settings.openai_api_key[:10] + "..." + settings.openai_api_key[-4:]
        print(f"   ✅ OPENAI_API_KEY is set: {key_preview}")

        # Check for quotes
        if settings.openai_api_key.startswith('"') or settings.openai_api_key.startswith("'"):
            print("   ❌ WARNING: API key starts with a quote character!")
            print("   ❌ Remove quotes from OPENAI_API_KEY in .env file")
            return False
        else:
            print("   ✅ API key format looks correct (no leading quotes)")
    else:
        print("   ❌ OPENAI_API_KEY is not set!")
        print("   ❌ Add OPENAI_API_KEY=your-key-here to .env file")
        return False

    # Check Embedding Provider
    print(f"\n2. Embedding Provider: {settings.embedding_provider}")
    if settings.embedding_provider.value == "openai":
        print("   ✅ Using OpenAI embeddings")
    else:
        print(f"   ℹ️  Using {settings.embedding_provider} embeddings")

    # Check Vector Store
    print(f"\n3. Vector Store Configuration:")
    print(f"   Type: {settings.vector_store.value}")

    if settings.vector_store.value == "chroma_cloud":
        if settings.chroma_cloud_api_key:
            key_preview = settings.chroma_cloud_api_key[:10] + "..." + settings.chroma_cloud_api_key[-4:]
            print(f"   ✅ CHROMA_CLOUD_API_KEY is set: {key_preview}")

            # Check for quotes
            if settings.chroma_cloud_api_key.startswith('"') or settings.chroma_cloud_api_key.startswith("'"):
                print("   ❌ WARNING: Chroma API key starts with a quote character!")
                print("   ❌ Remove quotes from CHROMA_CLOUD_API_KEY in .env file")
                return False
        else:
            print("   ❌ CHROMA_CLOUD_API_KEY is not set!")
            return False

        print(f"   Host: {settings.chroma_cloud_host}:{settings.chroma_cloud_port}")
        if settings.chroma_cloud_tenant:
            print(f"   Tenant: {settings.chroma_cloud_tenant}")
        if settings.chroma_cloud_database:
            print(f"   Database: {settings.chroma_cloud_database}")
    else:
        print(f"   ✅ Using local/memory storage")

    # Check other settings
    print(f"\n4. Other Configuration:")
    print(f"   Chunk Size: {settings.chunk_size}")
    print(f"   Chunk Overlap: {settings.chunk_overlap}")
    print(f"   Max File Size: {settings.max_file_size_mb} MB")
    print(f"   Max Files Per Request: {settings.max_files_per_request}")

    print("\n" + "=" * 60)
    print("✅ All environment variables loaded correctly!")
    print("=" * 60)
    print("\nYou can now start the server with: python main.py")
    return True

if __name__ == "__main__":
    try:
        success = verify_env()
        if not success:
            print("\n❌ Configuration has errors. Please fix them before starting the server.")
            exit(1)
    except Exception as e:
        print(f"\n❌ Error loading configuration: {e}")
        print("\nMake sure:")
        print("1. .env file exists in the project root")
        print("2. Required variables are set (OPENAI_API_KEY)")
        print("3. Values are NOT wrapped in quotes")
        exit(1)
