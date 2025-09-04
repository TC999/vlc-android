import glob
for path in glob.glob('application/resources/src/main/res/values*/strings.xml'):
    with open(path, 'rb') as f:
        content = f.read()
    # 去除BOM头（如果有）
    if content.startswith(b'\xef\xbb\xbf'):
        content = content[3:]
        with open(path, 'wb') as f:
            f.write(content)
    else:
        print(f'No BOM found in {path}')