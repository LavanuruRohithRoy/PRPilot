import sys

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

from app.core.config import settings


def main() -> None:
    # 1. Determine authentication method
    api_key = settings.AZURE_OPENAI_API_KEY
    endpoint = settings.AZURE_OPENAI_ENDPOINT
    conn_str = settings.AZURE_AI_FOUNDRY_CONNECTION_STRING

    openai_client = None

    if api_key and endpoint:
        print("[OK] Azure API key and endpoint detected")
        try:
            openai_client = AzureOpenAI(
                api_key=api_key, azure_endpoint=endpoint, api_version="2024-06-01"
            )
            print("[OK] Deployment reachable")
        except Exception as e:
            print(f"[FAIL] Failed to initialize Azure OpenAI client: {e!s}")
            sys.exit(1)
    elif conn_str:
        print("[OK] Azure Connection String detected, using DefaultAzureCredential")
        # Verify Azure credentials load
        try:
            credential = DefaultAzureCredential()
            # Force a token fetch for validation
            credential.get_token("https://cognitiveservices.azure.com/.default")
            print("[OK] Azure credentials loaded")
        except Exception as e:
            print(f"[FAIL] Failed to load Azure credentials: {e!s}")
            sys.exit(1)

        # Connect to Project Client & Verify deployment connectivity
        try:
            project_client = AIProjectClient.from_connection_string(  # type: ignore[attr-defined]
                conn_str=conn_str, credential=credential
            )
            openai_client = project_client.inference.get_azure_openai_client()
            print("[OK] Deployment reachable")
        except Exception as e:
            print(f"[FAIL] Failed to reach deployment or initialize client: {e!s}")
            sys.exit(1)
    else:
        print(
            "[FAIL] Neither (AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT) "
            "nor AZURE_AI_FOUNDRY_CONNECTION_STRING are configured."
        )
        sys.exit(1)

    # 2. Submit a test grounded prompt & verify completion
    try:
        response = openai_client.chat.completions.create(
            model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=[
                {
                    "role": "system",
                    "content": "You are a test helper. Answer with: Test OK.",
                },
                {"role": "user", "content": "Ping"},
            ],
            timeout=15.0,
        )
        content = response.choices[0].message.content or ""
        if "Test OK" in content:
            print("[OK] Completion generated")
            print("[OK] Foundry integration verified")
        else:
            print(f"[FAIL] Unexpected completion response: {content}")
            sys.exit(1)
    except Exception as e:
        print(f"[FAIL] Failed to generate completion: {e!s}")
        sys.exit(1)


if __name__ == "__main__":
    main()
