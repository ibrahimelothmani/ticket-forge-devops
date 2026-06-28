import os
import sys
import time
import requests

# 1. إعداد المتغيرات الأساسية من الـ Environment Variables لأمان مطلق
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

REPO_OWNER = "Ibrahim-ElOthmani"
REPO_NAME = "ticket-forge-devops"
WORKFLOW_FILE = "ticket-service-ci.yml"

GITHUB_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{WORKFLOW_FILE}/runs"

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github+json",
}

def send_slack_notification(status, conclusion, commit_msg, run_url, run_id):
    """إرسال تنبيه احترافي ومنسق وملون إلى Slack Workspace"""
    if not SLACK_WEBHOOK_URL:
        print("⚠️ [Slack] Webhook URL not configured. Skipping notification.")
        return

    # تحديد الألوان والحالات بناءً على النتيجة
    if status in ["queued", "in_progress"]:
        color = "#f2c744"  # أصفر للـ Processing
        title = "⏳ CI/CD Pipeline Build: IN PROGRESS"
        emoji = "🔄"
    elif status == "completed" and conclusion == "success":
        color = "#2eb886"  # أخضر للـ Success
        title = "✅ CI/CD Pipeline Build: SUCCESS"
        emoji = "🚀"
    else:
        color = "#a30200"  # أحمر للـ Failure
        title = "🚨 CI/CD Pipeline Build: CRITICAL FAILURE"
        emoji = "💥"

    # هيكلة الـ Payload بتصميم Dragon-Level لتسهيل القراءة
    payload = {
        "text": f"{emoji} *TicketForge Deployment Alert*",
        "attachments": [
            {
                "color": color,
                "title": title,
                "title_link": run_url,
                "fields": [
                    {"title": "Repository", "value": f"{REPO_OWNER}/{REPO_NAME}", "short": True},
                    {"title": "Run ID", "value": f"#{run_id}", "short": True},
                    {"title": "Commit Message", "value": f"_{commit_msg}_", "short": False},
                    {"title": "Pipeline Status", "value": f"*{status.upper()}* ({conclusion.upper() if conclusion else 'PENDING'})", "short": False}
                ],
                "footer": "Future Eagle IoT Automation Engine",
                "ts": int(time.time())
            }
        ]
    }

    try:
        res = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
        if res.status_code == 200:
            print("📱 [Slack] Live notification broadcasted successfully.")
        else:
            print(f"⚠️ [Slack] Failed to send notification. Response: {res.text}")
    except Exception as e:
        print(f"❌ [Slack] Connection error: {e}")


def get_latest_pipeline_run():
    params = {"branch": "main", "per_page": 1}
    try:
        response = requests.get(GITHUB_API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        runs = response.json().get("workflow_runs", [])
        return runs[0] if runs else None
    except Exception as e:
        print(f"❌ Failed to connect to GitHub API: {e}")
        return None

def monitor_ci_cd():
    print("🤖 [ChatOps Monitor] Booting TicketForge Suite...")
    latest_run = get_latest_pipeline_run()
    if not latest_run:
        sys.exit(1)
        
    run_id = latest_run["id"]
    html_url = latest_run["html_url"]
    current_status = latest_run["status"]
    conclusion = latest_run["conclusion"]
    commit_msg = latest_run["head_commit"]["message"]

    # إرسال التنبيه الأول: الـ Pipeline انطلق الآن!
    send_slack_notification(current_status, conclusion, commit_msg, html_url, run_id)

    # حلقة المراقبة والـ Polling
    while current_status in ["queued", "in_progress"]:
        print(f"🔄 Waiting for Pipeline #{run_id} to complete...")
        time.sleep(20)
        
        run_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}"
        try:
            res = requests.get(run_url, headers=headers, timeout=10)
            run_data = res.json()
            current_status = run_data["status"]
            conclusion = run_data["conclusion"]
        except Exception as e:
            print(f"⚠️ Error during polling: {e}")

    # إرسال التنبيه الأخير: النتيجة النهائية (أخضر أو أحمر)
    send_slack_notification(current_status, conclusion, commit_msg, html_url, run_id)

    if current_status == "completed" and conclusion == "success":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    monitor_ci_cd()