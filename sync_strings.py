import os
import glob
from lxml import etree as ET

def sync_strings():
    # 设置主strings.xml路径
    res_dir = os.path.join('application', 'resources', 'src', 'main', 'res')
    main_values_dir = os.path.join(res_dir, 'values')
    main_strings_path = os.path.join(main_values_dir, 'strings.xml')
    
    # 检查主文件是否存在
    if not os.path.exists(main_strings_path):
        print(f"主strings.xml文件不存在: {main_strings_path}")
        return
    
    # 解析主strings.xml
    try:
        parser = ET.XMLParser(remove_blank_text=True, resolve_entities=False, remove_comments=False)
        main_tree = ET.parse(main_strings_path, parser=parser)
        main_root = main_tree.getroot()
    except Exception as e:
        print(f"解析主strings.xml失败: {e}")
        return
    
    # 提取主文件中的<string>元素，保留顺序
    main_strings_order = []
    main_strings = {}
    for string_elem in main_root.findall('string'):
        name = string_elem.get('name')
        if name:
            main_strings[name] = string_elem.text
            main_strings_order.append(name)
    
    # 获取所有values-*目录
    language_dirs = glob.glob(os.path.join(res_dir, 'values-*'))
    
    for lang_dir in language_dirs:
        # 构建目标strings.xml路径
        target_strings_path = os.path.join(lang_dir, 'strings.xml')
        
        # 跳过不存在的文件
        if not os.path.exists(target_strings_path):
            print(f"跳过不存在的文件: {target_strings_path}")
            continue
        
        # 读取原始XML声明
        original_declaration = None
        try:
            with open(target_strings_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('<?xml') and first_line.endswith('?>'):
                    original_declaration = first_line + '\n'
        except Exception as e:
            print(f"读取XML声明失败 {target_strings_path}: {e}")

        # 解析目标strings.xml
        try:
            parser = ET.XMLParser(remove_blank_text=True, resolve_entities=False, remove_comments=False)
            target_tree = ET.parse(target_strings_path, parser=parser)
            target_root = target_tree.getroot()
        except Exception as e:
            print(f"解析目标文件失败 {target_strings_path}: {e}")
            continue
        
        # 提取目标文件中的<string>元素name属性
        target_names = set()
        for string_elem in target_root.findall('string'):
            name = string_elem.get('name')
            if name:
                target_names.add(name)
        
        # 添加缺失的<string>元素并保持顺序
        added_count = 0
        target_string_positions = {}
        target_strings_order = []
        for pos, elem in enumerate(target_root):
            if elem.tag == 'string' and elem.get('name'):
                name = elem.get('name')
                target_string_positions[name] = pos
                target_strings_order.append(name)

        # 跟踪已插入元素以调整位置
        inserted_count = 0
        for main_idx, name in enumerate(main_strings_order):
            if name not in target_names:
                # 查找插入位置
                # 计算在目标字符串序列中的插入位置
                insert_seq_idx = 0
                for seq_idx, target_name in enumerate(target_strings_order):
                    try:
                        target_main_idx = main_strings_order.index(target_name)
                    except ValueError:
                        continue
                    if target_main_idx < main_idx:
                        insert_seq_idx = seq_idx + 1
                    else:
                        break

                # 计算绝对插入位置
                if insert_seq_idx < len(target_strings_order):
                    insert_pos = target_string_positions[target_strings_order[insert_seq_idx]]
                else:
                    insert_pos = target_string_positions[target_strings_order[-1]] + 1 if target_strings_order else 0

                # 调整已插入元素导致的位置偏移
                insert_pos += inserted_count
                # 创建并插入新元素
                new_elem = ET.Element('string', name=name)
                new_elem.text = main_strings[name]
                target_root.insert(insert_pos, new_elem)
                inserted_count += 1
                added_count += 1
                print(f"添加 {name} 到 {target_strings_path} (位置: {insert_pos})")
                # 更新目标字符串序列和位置映射
                target_strings_order.insert(insert_seq_idx, name)
                target_string_positions[name] = insert_pos
        
        # 如果有添加，保存文件
        if added_count > 0:
            try:
                # 写入文件，保留XML声明和编码
                # 保留原始XML声明和格式
                with open(target_strings_path, 'wb') as f:
                    if original_declaration:
                        f.write(original_declaration.encode('utf-8'))
                    # 写入XML内容，不带声明
                    xml_content = ET.tostring(target_root.getroottree(), encoding='utf-8', xml_declaration=False, pretty_print=True)
                    f.write(xml_content)
                print(f"已更新 {target_strings_path}，添加了 {added_count} 个条目")
            except Exception as e:
                print(f"写入文件失败 {target_strings_path}: {e}")

def main():
    sync_strings()

if __name__ == "__main__":
    main()