import os
import subprocess
import requests

def main():
    api_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPEN_ROUTER_KEY")
    gh_token = os.environ.get("GH_TOKEN")
    pr_number = os.environ.get("PR_NUMBER")
    repo = os.environ.get("REPO")
    base_sha = os.environ.get("BASE_SHA", "origin/master")
    head_sha = os.environ.get("HEAD_SHA", "HEAD")
    model = os.environ.get("AI_MODEL", "nvidia/nemotron-3.5-super-vl:free")

    if not api_key:
        print("Missing OPENROUTER_API_KEY / OPEN_ROUTER_KEY. Skipping review.")
        return

    if not pr_number:
        print("Missing PR_NUMBER. Skipping review.")
        return

    # 1. Fetch git diff
    diff = subprocess.check_output(
        ["git", "diff", f"{base_sha}...{head_sha}"],
        text=True,
        errors="ignore"
    )

    if not diff.strip():
        print("No changes found in diff.")
        return

    # Cap diff to prevent exceeding token limits if changes are huge
    max_diff_len = 16000
    if len(diff) > max_diff_len:
        diff = diff[:max_diff_len] + "\n\n...[diff truncated for length]..."

    prompt = (
        "You are a senior software engineer performing a code review on a GitHub Pull Request.\n"
        "Provide constructive feedback, identify potential bugs, security issues, performance pitfalls, "
        "and suggest code improvements.\n\n"
        f"Git Diff:\n```diff\n{diff}\n```"
    )

    # 2. Call OpenRouter API
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": f"https://github.com/{repo}",
            "X-Title": "GitHub Actions Auto Review",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a professional code reviewer."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        },
        timeout=120
    )
    if not response.ok:
        print(f"OpenRouter API error ({response.status_code}): {response.text}")
    response.raise_for_status()
    review_content = response.json()["choices"][0]["message"]["content"]

    # 3. Post review comment to the Pull Request
    gh_headers = {
        "Authorization": f"Bearer {gh_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    comment_body = f"### 🤖 AI Code Review (via OpenRouter - `{model}`)\n\n{review_content}"

    post_comment_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    resp = requests.post(post_comment_url, headers=gh_headers, json={"body": comment_body})
    resp.raise_for_status()
    print("Successfully posted review comment!")

if __name__ == "__main__":
    main()
