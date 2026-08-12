"""
Dataset loader — fetches legal documents from Indian Kanoon API.
Falls back to local JSON files if API token is not configured or API is unreachable.

Updated:
- Generates embeddings for loaded documents.
- Stores embeddings as JSON string.
"""

import json
from pathlib import Path

from loguru import logger
from sqlalchemy.orm import Session

from app.core.config import get_settings

from app.models.legal_document import (
    LegalDocument,
    DocumentCategory
)

from app.repositories import document_repository

from app.services.embedding_service import EmbeddingService


settings = get_settings()


embedding_service = EmbeddingService()


DATASET_ROOT = Path(__file__).parent.parent / "dataset"



_API_QUERIES: list[tuple[str, DocumentCategory]] = [

    (
        "Constitution of India",
        DocumentCategory.ACT
    ),

    (
        "Indian Penal Code",
        DocumentCategory.ACT
    ),

    (
        "Code of Criminal Procedure",
        DocumentCategory.ACT
    ),

    (
        "Information Technology Act",
        DocumentCategory.ACT
    ),

    (
        "Protection of Women from Domestic Violence Act",
        DocumentCategory.ACT
    ),

    (
        "Kesavananda Bharati Supreme Court",
        DocumentCategory.LANDMARK_CASE
    ),

    (
        "Maneka Gandhi Supreme Court",
        DocumentCategory.LANDMARK_CASE
    ),

    (
        "Vishaka v State of Rajasthan",
        DocumentCategory.LANDMARK_CASE
    ),

    (
        "Indira Sawhney Supreme Court reservation",
        DocumentCategory.LANDMARK_CASE
    ),

    (
        "Shreya Singhal Section 66A",
        DocumentCategory.LANDMARK_CASE
    ),

    (
        "Supreme Court judgment criminal appeal 2023",
        DocumentCategory.JUDGMENT
    ),

    (
        "High Court judgment civil dispute 2023",
        DocumentCategory.JUDGMENT
    )

]



_FOLDER_MAP = [

    (
        "acts",
        DocumentCategory.ACT
    ),

    (
        "landmark_cases",
        DocumentCategory.LANDMARK_CASE
    ),

    (
        "judgments",
        DocumentCategory.JUDGMENT
    )

]



# -------------------------------------------------
# MAIN LOADER
# -------------------------------------------------

def load_all(db: Session):

    token = settings.INDIAN_KANOON_API_TOKEN.strip()


    if token:

        total = _load_from_api(
            db,
            token
        )

    else:

        logger.warning(
            "INDIAN_KANOON_API_TOKEN not set — using local dataset"
        )


        total = _load_from_local(
            db
        )



    logger.info(
        "DatasetLoader finished — {} records inserted",
        total
    )





# -------------------------------------------------
# API LOADER
# -------------------------------------------------

def _load_from_api(
    db: Session,
    token: str
):

    try:

        import httpx

    except ImportError:

        logger.error(
            "httpx missing"
        )

        return _load_from_local(db)



    total = 0


    headers = {
        "Authorization": f"Token {token}"
    }



    with httpx.Client(timeout=15) as client:


        for query, category in _API_QUERIES:


            try:


                response = client.post(

                    "https://api.indiankanoon.org/search/",

                    headers=headers,

                    data={
                        "formInput": query,
                        "pagenum": 0
                    }

                )



                if response.status_code != 200:

                    logger.warning(
                        "API failed {}",
                        query
                    )

                    continue



                results = response.json().get(
                    "docs",
                    []
                )



                for item in results[:3]:

                    total += _upsert_api_doc(

                        db,
                        item,
                        category

                    )


            except Exception as e:

                logger.error(
                    "API error {}",
                    e
                )



    return total






def _upsert_api_doc(
    db: Session,
    item: dict,
    category: DocumentCategory
):


    source_file = (
        f"ik_{item.get('tid','')}.json"
    )



    if document_repository.exists_by_source_and_category(

        db,

        source_file,

        category

    ):

        return 0




    title = (
        item.get("title")
        or
        item.get("headline")
        or
        source_file
    )



    description = _strip_html(

        item.get(
            "headline",
            ""
        )

    )



    embedding_text = (

        title

        + " "

        + description

    )



    embedding = embedding_service.embed(

        embedding_text

    )



    doc = LegalDocument(


        title=title,


        source_file=source_file,


        category=category,


        description=description,


        citation=item.get(
            "citation"
        ),


        year=_parse_year(

            item.get(
                "publishdate",
                ""
            )

        ),


        court=item.get(
            "docsource"
        ),


        source=(

            f"https://indiankanoon.org/doc/"
            f"{item.get('tid','')}/"

        ),


        tags=",".join(

            item.get(
                "categories",
                []
            )

        ) or None,


        file_type="API",


        embedding=json.dumps(
            embedding
        )

    )



    document_repository.create_document(

        db,

        doc

    )


    logger.info(
        "Loaded API document {}",
        title
    )


    return 1






# -------------------------------------------------
# LOCAL DATASET LOADER
# -------------------------------------------------

def _load_from_local(
    db: Session
):

    total = 0


    for folder, category in _FOLDER_MAP:


        total += _load_folder(

            db,

            DATASET_ROOT / folder,

            category

        )


    return total






def _load_folder(
    db: Session,
    folder: Path,
    category: DocumentCategory
):


    if not folder.exists():

        logger.warning(
            "Folder missing {}",
            folder
        )

        return 0



    count = 0



    for file in folder.iterdir():


        if not file.is_file():

            continue



        try:


            if document_repository.exists_by_source_and_category(

                db,

                file.name,

                category

            ):

                continue




            if file.suffix == ".json":


                doc = _build_from_json(

                    file,

                    category

                )



            elif file.suffix == ".pdf":


                doc = _build_from_pdf(

                    file.name,

                    category

                )


            else:

                continue




            document_repository.create_document(

                db,

                doc

            )



            count += 1



            logger.info(

                "Loaded {}",

                file.name

            )



        except Exception as e:


            logger.error(

                "Failed {} : {}",

                file.name,

                e

            )



    return count






# -------------------------------------------------
# BUILD JSON DOCUMENT
# -------------------------------------------------

def _build_from_json(
    file: Path,
    category: DocumentCategory
):


    with open(
        file,
        encoding="utf-8"
    ) as f:


        meta = json.load(f)



    title = (
        meta.get("title")
        or
        file.name
    )



    description = (
        meta.get("description")
        or
        ""
    )



    tags = meta.get(
        "tags"
    ) or []



    judges = meta.get(
        "judges"
    ) or []



    tags_string = ",".join(

        tags + judges

    ) or None



    embedding_text = (

        title

        + " "

        + description

        + " "

        + (tags_string or "")

    )



    embedding = embedding_service.embed(

        embedding_text

    )



    return LegalDocument(


        title=title,


        short_title=meta.get(
            "shortTitle"
        ),


        source_file=file.name,


        category=category,


        description=description,


        citation=meta.get(
            "citation"
        ),


        year=meta.get(
            "year"
        ),


        court=meta.get(
            "court"
        ),


        source=meta.get(
            "source"
        ),


        tags=tags_string,


        file_type="JSON",


        embedding=json.dumps(
            embedding
        )

    )







# -------------------------------------------------
# BUILD PDF DOCUMENT
# -------------------------------------------------

def _build_from_pdf(
    filename: str,
    category: DocumentCategory
):


    title = (

        filename
        .replace(".pdf","")
        .replace("_"," ")
        .replace("-"," ")
        .title()

    )



    embedding = embedding_service.embed(

        title

    )



    return LegalDocument(


        title=title,


        source_file=filename,


        category=category,


        file_type="PDF",


        embedding=json.dumps(

            embedding

        )

    )






# -------------------------------------------------
# HELPERS
# -------------------------------------------------

def _strip_html(text: str):

    import re

    return re.sub(
        r"<[^>]+>",
        "",
        text
    ).strip()





def _parse_year(
    date_str: str
):

    try:

        return int(
            date_str[:4]
        ) if date_str else None


    except:

        return None