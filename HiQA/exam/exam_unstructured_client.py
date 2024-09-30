from dotenv import load_dotenv
import os
import sys
#import logging
import rich

load_dotenv()

if "./" not in sys.path:
    sys.path.append("./")

from HiQA.utils.util_logging import setup_logger_handlers
#from HiQA.utils.util_file import get_root_dir


# Before calling the API, replace filename and ensure sdk is installed: "pip install unstructured-client"
# See https://docs.unstructured.io/api-reference/api-services/sdk for more details

import unstructured_client
from unstructured_client.models import operations, shared

def test_unstructured(pdf_pathname, out_dir):
    client = unstructured_client.UnstructuredClient(
        api_key_auth=os.environ.get("UNSTRUCTURED_KEY"),
        server_url=os.environ.get("UNSTRUCTURED_URL"),
    )

    filename = pdf_pathname
    with open(filename, "rb") as f:
        data = f.read()

    req = operations.PartitionRequest(
        partition_parameters=shared.PartitionParameters(
            files=shared.Files(
                content=data,
                file_name=filename,
            ),
            # --- Other partition parameters ---
            # Note: Defining 'strategy', 'chunking_strategy', and 'output_format'
            # parameters as strings is accepted, but will not pass strict type checking. It is
            # advised to use the defined enum classes as shown below.
            #content_type="markdown",
            strategy=shared.Strategy.HI_RES,  
            languages=['chi_sim'],
            extract_image_block_types=["Image","Table"],
            #output_format="text/markdown"
        ),
    )

    res = client.general.partition(request=req)
    rich.print(res.elements[0])


if __name__ == "__main__":
    pdf_pathname = "datasrc/test/raw_docs/AIGC时代的人力资源管理进化(徐刚).pdf"
    #pdf_pathname = "datasrc/test/raw_docs/业绩案例、上汽内外饰DRE外包框架服务合同.pdf"
    out_dir = "_work/tmp"

    setup_logger_handlers()
    os.makedirs(out_dir, exist_ok=True)
    test_unstructured(pdf_pathname, out_dir)