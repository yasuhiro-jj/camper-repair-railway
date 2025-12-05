import os
from pathlib import Path

def fix_secrets():
    env_path = Path(".env")
    secrets_dir = Path(".streamlit")
    secrets_path = secrets_dir / "secrets.toml"

    if not env_path.exists():
        print("❌ .env file not found!")
        return

    if not secrets_dir.exists():
        secrets_dir.mkdir()

    print(f"Reading from {env_path}...")
    
    secrets_content = []
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                secrets_content.append(line)
                continue
            
            if "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                # Remove existing quotes if any
                if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                secrets_content.append(f'{key} = "{value}"')
            else:
                secrets_content.append(line)

    print(f"Writing to {secrets_path}...")
    with open(secrets_path, "w", encoding="utf-8") as f:
        f.write("\n".join(secrets_content))
    
    print("✅ secrets.toml created successfully!")

if __name__ == "__main__":
    fix_secrets()


