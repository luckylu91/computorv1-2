def root_str(root):
	if root == 0:
		return "0"
	return f"{root:.6f}".rstrip('0').rstrip('.')

def print_root(root):
	print(root_str(root))
