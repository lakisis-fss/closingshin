import re
text = "161.81-2.73%상승"
nums = re.findall(r'[0-9.,-]+', text)
print(f"Nums: {nums}")
print(f"Len: {len(nums)}")
