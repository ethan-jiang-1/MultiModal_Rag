import subprocess
import os
from dotenv import find_dotenv

def get_git_version() -> str:
    cur_dir = os.getcwd()

    root_dir = os.path.abspath(os.path.dirname(find_dotenv()))  

    gitv = None 
    os.chdir(root_dir)
    try:
        # 获取最新的tag
        tag = subprocess.check_output(['git', 'describe', '--tags'], stderr=subprocess.STDOUT).strip()
        gitv = tag.decode('utf-8')
    except subprocess.CalledProcessError:
        try:
            # 如果没有tag，获取最近的提交哈希
            commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD'], stderr=subprocess.STDOUT).strip()
            gitv = commit_hash.decode('utf-8')
        except Exception:
            gitv = "none0"
    except Exception:
        gitv = "none1"
    os.chdir(cur_dir)
    return gitv


if __name__ == "__main__":
    print(get_git_version())
