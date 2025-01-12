from typing import Optional, Tuple, Dict, List
from dotenv import load_dotenv
import os
import logging
import json
import re
from datetime import datetime
from pydantic import BaseModel, Field
from qdrant_client.http.models import CollectionInfo

load_dotenv()

from mrag_vdb.common.doc_meta_info import DocMetaInfo
from mrag_vdb.common.vdb_base import get_map_doc2col_pathname
from mmbase.utils.util_logging import setup_logger_handlers
from mrag_vdb.common.text_embedding import get_embedding_encoder_name, get_embeding_len

def decompose_doc_unique_id(doc_unique_id: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Decompose document unique ID into title and ID components.

    Args:
        doc_unique_id: Document unique identifier

    Returns:
        Tuple[Optional[str], Optional[str]]: (doc_title, unique_id) or (None, None) if invalid
    """
    pattern = r"^(.+?)_([a-f0-9]+)$"
    match = re.match(pattern, doc_unique_id)
    if match:
        return match.group(1), match.group(2)
    return None, None

class MapDocToCol(BaseModel):
    """
    Model for mapping documents to collections in vector database.
    """
    map_doc2col: Dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of document IDs to collection names"
    )
    lst_doc2col: List[Dict] = Field(
        default_factory=list,
        description="List of document to collection mapping details"
    )

    def save_to_file(self, path_map_doc2col: str) -> bool:
        """
        Save mapping to a JSON file.

        Args:
            path_map_doc2col: Path to save the mapping file

        Returns:
            bool: True if save was successful
        """
        dir_name = os.path.dirname(path_map_doc2col)
        os.makedirs(dir_name, exist_ok=True)
        with open(path_map_doc2col, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=4))
        return True

    @classmethod
    def load_from_file(cls, path_map_doc2col: str) -> 'MapDocToCol':
        """
        Load mapping from a JSON file.

        Args:
            path_map_doc2col: Path to the mapping file

        Returns:
            MapDocToCol: Loaded mapping object
        """
        if not os.path.isfile(path_map_doc2col):
            return cls(map_doc2col={}, lst_doc2col=[])
        with open(path_map_doc2col, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.model_validate(data)

    @classmethod
    def validate_doc_title(cls, md2c: 'MapDocToCol', doc_unique_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate document title uniqueness.

        Args:
            md2c: MapDocToCol instance
            doc_unique_id: Document unique identifier

        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        doc_title, unique_id = decompose_doc_unique_id(doc_unique_id)
        if doc_title is None:
            return False, f"invalid doc_unique_id: {doc_unique_id}"
        
        for key in md2c.map_doc2col.keys():
            if key.startswith(doc_title):
                if key != doc_unique_id:
                    return False, f"doc_unique_id_used: {doc_title} has defined in m2c already with {unique_id}"
        return True, None

    @classmethod
    def register_collection_name_for_doc(cls, doc_meta_info: DocMetaInfo, enforce_register:bool = False) -> str:
        """
        Register collection name for a document.

        Args:
            doc_meta_info: Document metadata information
            enforce_register: If True, enforce registration even if the document is already registered
        Returns:
            str: Collection name

        Raises:
            ValueError: If document validation fails
        """
        path_map_doc2col = get_map_doc2col_pathname()
        md2c = cls.load_from_file(path_map_doc2col)
        doc_unique_id = doc_meta_info.doc_unique_id

        valid, err = cls.validate_doc_title(md2c, doc_unique_id)
        if not valid:
            if enforce_register and err.startswith("doc_unique_id_used"):
                logging.warning(err + ", but enforce_register is True")
            else:
                raise ValueError(err)

        if doc_unique_id in md2c.map_doc2col:
            collection_name = md2c.map_doc2col[doc_unique_id]
            logging.info(f"existing map doc {doc_unique_id} to collection_name:{collection_name}")
        else:
            collection_name = doc_meta_info.collection_name
            md2c.map_doc2col[doc_unique_id] = collection_name
            logging.info(f"new map doc {doc_unique_id} to collection_name:{collection_name}")
            md2c.save_to_file(path_map_doc2col)

        return collection_name

    @classmethod
    def _construct_doc2col(
        cls, 
        doc_meta_info: DocMetaInfo, 
        collection_name: str, 
        collection: CollectionInfo, 
        item_added: int
    ) -> Dict:
        """
        Construct document to collection mapping details.

        Args:
            doc_meta_info: Document metadata
            collection_name: Collection name
            collection: Collection information
            item_added: Number of items added

        Returns:
            Dict: Mapping details
        """
        return {
            "collection_name": collection_name,
            "item_added": item_added,
            "vectors_size": collection.config.params.vectors.size,
            "embedding_encoder": get_embedding_encoder_name(),
            "embedding_len": get_embeding_len(),
            "doc_unique_id": doc_meta_info.doc_unique_id,
            "date_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def update_collection_name_for_doc(
        cls, 
        doc_meta_info: DocMetaInfo, 
        collection_name: str, 
        collection: CollectionInfo, 
        item_added: int
    ) -> None:
        """
        Update collection mapping for a document.

        Args:
            doc_meta_info: Document metadata
            collection_name: Collection name
            collection: Collection information
            item_added: Number of items added
        """
        path_map_doc2col = get_map_doc2col_pathname()
        d2c_info = cls.load_from_file(path_map_doc2col)
        
        update_item = cls._construct_doc2col(doc_meta_info, collection_name, collection, item_added)
        
        for item in d2c_info.lst_doc2col:
            if item["doc_unique_id"] == doc_meta_info.doc_unique_id:
                item.update(update_item)
                d2c_info.save_to_file(path_map_doc2col)
                return

        d2c_info.lst_doc2col.append(update_item)
        d2c_info.save_to_file(path_map_doc2col)


if __name__ == "__main__":
    from mrag_vdb.build._convert_doc_to_chunks import build_doc_meta_info, DocMetaInfo

    setup_logger_handlers()

    #pname_final_md_info = "_work/ctn2md_Survey_of_different_Large_Language_Model_Architectures_lvlm/_final_info.json"
    pname_final_md_info = "_work/ctn2md_papers__Survey_of_different_Large_Language_Model_Architectures_lvlm/_final_info.json"
    
    doc_meta_info = build_doc_meta_info(pname_final_md_info)

    collection_name_expected = None
    collection_name = MapDocToCol.register_collection_name_for_doc(doc_meta_info)
    print("regitered collection name: ", collection_name)

