import os

#TODO: hook unstructure_io
def generate_markdown_unstructured(md_info):
    doc_pathname = md_info.get_doc_pathname()
    if (doc_pathname is None) or (not os.path.isfile(doc_pathname)):
        raise ValueError(f"doc_pathname is not valid {doc_pathname}")

    raise ValueError("not implemented yet")