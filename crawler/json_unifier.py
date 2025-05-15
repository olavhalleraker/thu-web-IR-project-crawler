import os
import json

# Global variables
INPUT_FOLDER = 'articles'
OUTPUT_FILE = 'articles_database.json'

def unify_jsons_single_line_entries(input_folder, output_file):
    all_articles = []

    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            file_path = os.path.join(input_folder, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_articles.extend(data)
                    else:
                        all_articles.append(data)
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f_out:
            f_out.write('[\n')
            for i, article in enumerate(all_articles):
                json_line = json.dumps(article, ensure_ascii=False)
                comma = ',' if i < len(all_articles) - 1 else ''
                f_out.write(f'  {json_line}{comma}\n')
            f_out.write(']')
        print(f"Formatted JSON array written to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing output file: {e}")

if __name__ == '__main__':
    unify_jsons_single_line_entries(INPUT_FOLDER, OUTPUT_FILE)
