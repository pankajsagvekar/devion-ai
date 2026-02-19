import re

def clean_url(repo_url, token):
    if not token:
        return repo_url
    # Strip any existing credentials (everything between https:// and the last @ before the host)
    result = re.sub(r"https://[^/]*@", "https://", repo_url)
    if result.startswith("https://"):
        return result.replace("https://", f"https://{token}@")
    return result

test_cases = [
    ("https://github.com/user/repo", "TOKEN", "https://TOKEN@github.com/user/repo"),
    ("https://oldtoken@github.com/user/repo", "NEWTOKEN", "https://NEWTOKEN@github.com/user/repo"),
    ("https://token1@token2@github.com/user/repo", "NEWTOKEN", "https://NEWTOKEN@github.com/user/repo"),
    ("https://user:pass@github.com/user/repo", "NEWTOKEN", "https://NEWTOKEN@github.com/user/repo"),
]

for url, token, expected in test_cases:
    actual = clean_url(url, token)
    print(f"URL: {url}")
    print(f"Expected: {expected}")
    print(f"Actual:   {actual}")
    assert actual == expected
    print("MATCH!")
    print("-" * 20)
