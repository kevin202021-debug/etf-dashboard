import subprocess

scripts=["python/fetch_etf.py","python/load_to_sqlite.py","python/analyze_return.py","python/risk_analysis.py","python/portfolio_optimization.py","python/export_correlation.py"]

for script in scripts:
    print(f"\n執行{script}...")
    result=subprocess.run(["python",script],capture_output=True,text=True)

    print(result.stdout)

    if result.stderr:
        print(result.stderr)

print("\n流程完成!")        
