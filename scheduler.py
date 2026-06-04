import schedule
import time
import subprocess
from datetime import datetime

# =========================
# 執行資料更新流程
# =========================

def run_pipeline():

    print("\n====================")
    print("開始更新ETF資料")
    print(datetime.now())
    print("====================\n")

    try:

        result = subprocess.run(

            ["python", "python/master_pipeline.py"],

            capture_output=True,

            text=True
        )

        print(result.stdout)

        if result.stderr:

            print(result.stderr)

        print("\nETF資料更新完成！")

    except Exception as e:

        print(f"更新失敗: {e}")

# =========================
# 每日下午16:00執行
# =========================

schedule.every().day.at(
    "16:00"
).do(run_pipeline)

print("Scheduler 已啟動")
print("每日16:00自動更新ETF資料")

# =========================
# 持續監聽
# =========================

while True:

    schedule.run_pending()

    time.sleep(60)

