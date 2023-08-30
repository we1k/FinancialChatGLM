import json
import re
import ast
import os
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

root_directory = 'data/'
data_directory = 'data/lines_txt'

def read_dict_from_file(file_name):
    file_path = os.path.join(data_directory, file_name)
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = re.sub(r'<Page:\d+>', lambda match: f"'{match.group(0)}'", line)
            line_entry = ast.literal_eval(line.strip())
            yield line_entry

class ReportSplitter:
    def __init__(self, report_name):
        self.name = report_name 
        self.line_entries = []
        self.head_begin_pos = 0
        self.head_end_pos = 0
        self.section_infos = [{}]
        self.__init_entries()

    def __init_entries(self):
        for line_entry in read_dict_from_file(self.name):
            self.line_entries.append(line_entry)

    def extract_section_head(self):
        line_entries = self.line_entries
        head_pattern = r'^第(\D+)节(.*?)(?:\.{3,}\s*\d)?$'
        for idx in range(len(line_entries)):
            entry = line_entries[idx]
            content = entry['inside']
            head_idx = 0
            if '目录' in content:
                head_idx = idx + 1
                match_status = 0
                while True:
                    if match_status == 3:
                        break
                    head_content = line_entries[head_idx]['inside']
                    match = re.match(head_pattern, head_content)
                    if match:
                        match_status = 0
                        section_number = match.group(1)
                        section_title = match.group(2).strip() 
                        section_title = section_title.rstrip('.1234567890')
                        self.section_infos.append({'title':f"第{section_number}节{section_title}"})
                        head_idx += 1
                    else:
                        match_status += 1
                        head_idx += 1
                        continue
            if len(self.section_infos) > 1:
                self.head_begin_pos = idx # record the begin position of 'table of contents'
                self.head_end_pos = head_idx - 2
                break
    
    def write_folder(self):
        section_infos = self.section_infos
        line_entries = self.line_entries
        # write folder
        dir_head = self.name[:-4]
        dir_path = os.path.join('data', 'section_dirs', dir_head)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        else:
            print(f"[INFO] folder '{dir_path}' exists, skipped")

        # write section txt
        for sec_num in range(1, len(section_infos)):
            section_info = section_infos[sec_num]
            begin_pos = section_info['pos']
            if sec_num == len(section_infos) - 1:
                end_pos = len(line_entries) + 1
            else:
                end_pos = section_infos[sec_num+1]['pos']
            section_file_name = f"{section_info['title']}.txt"
            txt_data = '\n'.join([str(d) for d in line_entries[begin_pos:end_pos]])
            # print(section_file_name, sec_num, begin_pos, end_pos)
            section_file_path = os.path.join(dir_path, section_file_name)
            if not os.path.exists(section_file_path):
                with open(section_file_path, 'w', encoding='utf-8') as file:
                    file.write(txt_data)

    def split_sections(self):
        self.extract_section_head()
        # search each section position
        head_begin_pos = self.head_begin_pos
        head_end_pos = self.head_end_pos
        line_entries = self.line_entries
        section_infos = self.section_infos
        if len(section_infos) == 1:
            print(f"[ERROR] The format of {self.name} is special")
            return
        cur_section = 1
        cur_section_title = section_infos[cur_section]['title']
        for idx in range(len(line_entries)):
            if idx >= head_begin_pos and idx <= head_end_pos:  # jump out table of contents
                continue
            entry = line_entries[idx]
            content = entry['inside']
            if content.find(cur_section_title) != -1:
                section_infos[cur_section]['pos'] = idx
                # search next section
                cur_section += 1
                if cur_section >= len(section_infos):
                    break
                cur_section_title = section_infos[cur_section]['title']
        self.write_folder()
        # print(section_infos)
        # print("")




# file_name = '2021-04-29__江苏银行股份有限公司__600919__江苏银行__2020年__年度报告.txt'
# splitter = ReportSplitter(file_name)
# splitter.split_sections()


file_names = os.listdir(data_directory)

total_files_len = len(file_names) 
progress_bar = tqdm(total=total_files_len, desc='Processing files', unit='file', ncols=80, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}')


def process_file(file_name):
    splitter = ReportSplitter(file_name)
    splitter.split_sections()

with ProcessPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(process_file, file_name) for file_name in file_names]

    for future in tqdm(as_completed(futures), total=total_files_len):
        try:
            result = future.result()
            progress_bar.set_postfix(file=result)
        except Exception as e:
            print(f"Exception occurred: {e}")

        progress_bar.update(1)

progress_bar.close()