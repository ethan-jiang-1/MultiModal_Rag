import sys

sys.path.append("./")

#from dotenv import load_dotenv
import os
#import tiktoken
import pandas as pd
import logging

# note that this is in version openai==0.28, if you update to >=1.0.0, you need to create OpenAI() object.
from example.api_warpper import get_text_embedding
from HiQA.utils.tokenizer import get_token_encoding
from HiQA.utils.openai_proxy import EMBEDDING_MODEL

OPENAI_EMBEDDING_MAXTOKENS = 8000


def split_and_embed(section, encoding):
    # Get the title from the first line
    lines = section.split("\n")
    title = lines[0]
    content = "\n".join(lines[1:])

    half_length = len(content) // 2
    section_1 = title + "\n" + content[:half_length]
    section_2 = title + "\n" + content[half_length:]

    sections = [section_1, section_2]

    new_sections = []

    for sec in sections:
        if len(encoding.encode(sec)) > OPENAI_EMBEDDING_MAXTOKENS:
            new_sections.extend(split_and_embed(sec, encoding))
        else:
            new_sections.append(sec)

    return new_sections


def section_to_embed(file_path, output_folder):

    name = os.path.basename(file_path).split(".csv")[0]

    # embed_path = os.path.join(BASE_DIR, 'file_system', kb_name, 'embedded')
    df = pd.read_csv(file_path, encoding='utf-8')
    encoding = get_token_encoding()

    new_df_entries = []

    import tqdm
    for _, row in tqdm.tqdm(df.iterrows()):
        section = row['section']
        n_tokens = len(encoding.encode(section))

        if '---table begin---' in section:
            # Get the content before and after the table as well as the table's title, column names, and row names
            table_start_idx = section.find('---table begin---')
            table_end_idx = section.find('---table end---') + len(
                '---table end---')

            # Get the metadata before the table
            pre_table_content = section[:table_start_idx]

            # Get the table title
            table_title_start = table_start_idx + len('---table begin---')
            table_title_line = section[table_title_start:section.
                                       find('\n', table_title_start +
                                            1)].replace('Table title:',
                                                        '').replace(
                                                            'Table tile:',
                                                            '').strip()

            # print('title:', table_title_line)
            # Extract the table content and split into lines
            table_content = section[table_start_idx +
                                    len('---table begin---'
                                        ):table_end_idx].split('\n')[1:-1]
            # print(table_content)
            # Get the table headers (column names)
            try:
                table_headers = table_content[1].strip().split('|')[
                    1:-1]  # Exclude the first and last empty items
            except IndexError as e:
                logging.exception(e)
                # print(section.find('---table begin---'), section.find('---table end---'))
                # print(section + '\n----sec---\n')
                continue
            # print(table_headers)
            table_headers = [header.strip() for header in table_headers]
            # print(table_headers)
            # Get the row names (assuming they are in the first column)
            table_row_names = []
            for row_content in table_content[3:]:
                if row_content[0] == '|':
                    table_row_names.append(row_content.split('|')[1].strip())
            # Embed metadata content
            metadata_content = '\n'.join(
                [pre_table_content, table_title_line] + table_headers +
                table_row_names)
            # print('\n-------TABLE FOUND--------\n content:\n'+section+'\n metadata:\n'+metadata_content+'\n--------------------------\n')

            actual_section = section.replace('---table begin---', '').replace(
                '---table end---', '')
            new_df_entries.append({
                'section':
                actual_section,
                'n_tokens':
                len(encoding.encode(metadata_content)),
                'embedding':
                get_text_embedding(metadata_content, deployment=EMBEDDING_MODEL)
            })

        else:
            if n_tokens < OPENAI_EMBEDDING_MAXTOKENS:
                new_df_entries.append({
                    'section':
                    section,
                    'n_tokens':
                    n_tokens,
                    'embedding':
                    get_text_embedding(section, deployment=EMBEDDING_MODEL)
                })
            else:
                for new_section in split_and_embed(section, encoding):
                    new_df_entries.append({
                        'section':
                        new_section,
                        'n_tokens':
                        len(encoding.encode(new_section)),
                        'embedding':
                        get_text_embedding(new_section, deployment=EMBEDDING_MODEL)
                    })

    df_new = pd.DataFrame(new_df_entries)

    csv_embd_path = os.path.join(output_folder, name.replace('.md', '.csv'))
    df_new.to_csv(csv_embd_path, index=False, encoding='utf-8')
    logging.info(f"embd_csv: {csv_embd_path} saved, csv_columns: {df_new.columns}")
    return csv_embd_path


# section_to_embed('1. 座椅STO间隙 P1.pptx.step1.md.csv')
