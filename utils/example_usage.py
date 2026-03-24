# © 2026 MirageShield 团队 版权所有，侵权必究
from code_diff import count_deleted_lines, count_deleted_lines_from_files

# 示例 1: 直接比较字符串
old_code = '''
def hello():
    print("Hello, world!")
    print("This is a test")
    return "Hello"
'''

new_code = '''
def hello():
    print("Hello, world!")
    return "Hello"
'''

deleted = count_deleted_lines(old_code, new_code)
print(f"删除的行数: {deleted}")

# 示例 2: 比较文件
# 首先创建两个测试文件
with open('old_file.py', 'w') as f:
    f.write('line 1\nline 2\nline 3\nline 4\nline 5')

with open('new_file.py', 'w') as f:
    f.write('line 1\nline 4')

deleted_from_files = count_deleted_lines_from_files('old_file.py', 'new_file.py')
print(f"从文件中删除的行数: {deleted_from_files}")
