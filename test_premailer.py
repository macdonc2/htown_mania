from premailer import transform

html = """
<html>
<head>
<style>
    .red { color: red; background: yellow; }
</style>
</head>
<body>
    <div class="red">This should be red text on yellow background</div>
</body>
</html>
"""

print("BEFORE PREMAILER:")
print(html)
print("\n" + "="*80 + "\n")

result = transform(html)
print("AFTER PREMAILER:")
print(result)
