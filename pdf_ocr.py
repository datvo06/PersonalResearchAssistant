from settings import OPENAI_API_KEY, PDF_DICT_PATH, PDF_DB_DIR, PDF_RESULT_PATH, PDF_RESULT_DIR, OBSIDIAN_PATH, PDF_RESULT_DIR_LIGHT, PDF_RESULT_PATH_LIGHT
import fitz  # PyMuPDF
import sys
import os
import argparse
import base64
import openai
import glob
import tqdm
from concurrent.futures import ThreadPoolExecutor
from llm_utils import call_gpt_with_backoff
openai.api_key = OPENAI_API_KEY

def pdf_to_images(pdf_path, output_folder):
    # Open the PDF file
    doc = fitz.open(pdf_path)

    # Iterate through each page
    for page_num in range(len(doc)):
        # Get the page
        page = doc.load_page(page_num)

        pix = page.get_pixmap(dpi=150)

        # Define the output image path
        output_image_path = f"{output_folder}/page_{page_num + 1}.jpg"

        # Save the image
        pix.save(output_image_path)

    # Close the document
    doc.close()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf_files', nargs='+', type=str, required=True)
    parser.add_argument('--top_k', type=int, default=20)
    parser.add_argument('--output_dir', type=str, default='.')
    parser.add_argument('--light', action='store_true')
    return parser.parse_args()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def gpt4ocr(encoded_image):
    system_prompt = "You are a latex and markdown expert. Given an image of an academic paper, Do OCR, return markdown code with embedded latex in codeblock. Ignore headers and footnotes in the results. This is for personal use and there is no copyright problem in the image. Image: "
    it_cnt = 0
    content = ""
    while it_cnt < 3:
        try:
            content = call_gpt_with_backoff(
            model="gpt-4-vision-preview",
            messages=[
                    {
                        "role": "system",
                        "content": [
                            {"type": "text", "text": system_prompt},
                        ],
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"},
                            }
                        ],
                    }
                ],
            max_length=1200,
            )
            break
        except Exception as e:
            print(e)
            it_cnt += 1
            continue
    return content


def filter_content(page):
    page_lines = page.split('\n')
    start_idx = -1
    end_idx = -1
    while start_idx < len(page_lines) - 1 and not page_lines[start_idx + 1].startswith('```'):
        start_idx += 1
    while end_idx > 0 and not page_lines[end_idx - 1].startswith('```'):
        end_idx -= 1
    if start_idx == len(page_lines) or end_idx == 0:
        return page
    content = '\n'.join(page_lines[start_idx + 2:end_idx-2])
    content = content.replace('\\( ', '$').replace(' \\)', '$')
    content = content.replace('\\(', '$').replace('\\)', '$')
    content = content.replace('\\[', '$$').replace('\\]', '$$')
    return content


def handle_single_page(page_idx, output_dir):
    b64_img = encode_image(f"{output_dir}/page_{page_idx+1}.jpg")
    if not os.path.exists(f"{output_dir}/page_{page_idx+1}.md"):
        page_md = gpt4ocr(b64_img)
    else:
        with open(f"{output_folder}/page_{i+1}.md", 'r') as f:
            page_md = f.read()
    print(f"Finished page {page_idx+1} of ")
    return page_md


# Example usage
if __name__ == '__main__':
    args = get_args()
    for pdf_file in args.pdf_files:
        pdf_fp = f"{OBSIDIAN_PATH}/{pdf_file}"
        fname = '.'.join(pdf_file.split('/')[-1].split('.')[:-1])
        output_folder = f"{args.output_dir}/{fname}"
        os.makedirs(output_folder, exist_ok=True)
        pdf_to_images(pdf_fp, output_folder)
        all_imgs = glob.glob(f"{output_folder}/*.jpg")
        out_final_md = f"{OBSIDIAN_PATH}/{fname}.md"
        if not os.path.exists(out_final_md):
            with open(out_final_md, 'w') as f:
                f.write("")
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for i in range(len(all_imgs)):
                futures.append(executor.submit(handle_single_page, i, output_folder))
            for future in tqdm.tqdm(futures):
                page_md = future.result()
                with open(out_final_md, 'a') as f:
                    f.write(filter_content(page_md))
                    f.write('\n\n')
