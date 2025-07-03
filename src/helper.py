def save_urls_to_text_file(html_urls, pdf_urls: list, directory_name):
    with open(f"pdf_urls_{directory_name}.txt", "w", encoding="utf-8") as f:
        for url in pdf_urls:
            f.write(url + "\n")

    with open(f"html_urls_{directory_name}.txt", "w", encoding="utf-8") as f:
        for url in html_urls:
            f.write(url + "\n")

    return f"html_urls_{directory_name}.txt", f"pdf_urls_{directory_name}.txt"