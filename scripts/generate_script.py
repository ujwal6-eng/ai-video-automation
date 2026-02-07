import datetime

now = datetime.datetime.utcnow().isoformat()

print("✅ GitHub Actions is working")
print("🕒 Time (UTC):", now)

with open("test_output.txt", "w") as f:
    f.write(f"Pipeline ran successfully at {now}\n")

print("📄 test_output.txt file created")
