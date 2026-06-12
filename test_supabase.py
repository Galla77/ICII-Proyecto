import subprocess
import sys

def test_combination(supabase_ver, httpx_ver):
    print(f"Testing supabase=={supabase_ver} with httpx=={httpx_ver}")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", f"supabase=={supabase_ver}", f"httpx=={httpx_ver}"])
    result = subprocess.run([sys.executable, "-c", "from supabase import create_client; create_client('http://localhost', 'key')"], capture_output=True, text=True)
    if result.returncode == 0:
        print("SUCCESS")
    else:
        print("FAILED:")
        print(result.stderr.splitlines()[-1])
    print("-" * 40)

test_combination("2.3.4", "0.25.2")
test_combination("2.3.4", "0.24.0")
test_combination("latest", "latest")
