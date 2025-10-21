import io
from time import sleep
import time
from typing import List, Dict, Optional, Any, Sequence
# Removed PyPDF2 import as we're now using pymupdf4llm
import logging
from PyPDF2 import PdfReader
from openai import BadRequestError, RateLimitError
import pandas as pd
import re
import base64
import fitz
from pyparsing import Enum

# Importing from monkai_shared
from monkai_shared.agent.ai_manager import AzureRegion
from monkai_shared.analyzers.query import Query, Questionnaire, PropositionType

from monkai_shared.agent.engines.query_engine import QueryEngine
import monkai_shared.analyzers.tools as vtools
# Langchain imports
from langchain.vectorstores import faiss
from langchain.schema.document import Document
from pydantic import BaseModel
# Import the config for OpenAI settings
import config
from monkai_shared.analyzers.classifier_parameter import ClassifierParameter, IndexerField
       
class PDFWrongFromat(Exception):
    """Exception raised when an invalid PDF format is found."""
    pass

def get_page(response):
    """
    Gets the page labels from the response.

    Args:
        response: The response containing source nodes.

    Returns:
        str: A string with unique page labels, separated by commas.
            If there are no source nodes, returns '0'.
    """
    if not hasattr(response, 'source_documents') or not response.source_documents:
        return '0'
    
    unique_page_labels = set()
    for doc in response.source_documents:
        # Handle different document structures
        if hasattr(doc, 'metadata'):
            page_label = doc.metadata.get('page')
            if page_label:
                unique_page_labels.add(str(page_label))
        # Handle PDFMarkdownReader document structure
        elif hasattr(doc, 'extra_info'):
            page_label = doc.extra_info.get('page')
            if page_label:
                unique_page_labels.add(str(page_label))
    
    return ', '.join(sorted(unique_page_labels)) if unique_page_labels else '0'

def remove_special_characters(text):
    """
    Removes special characters from a string.

    Args:
        text (str): The input string from which special characters will be removed.

    Returns:
        str: The input string without special characters.
    """
    # Define a regular expression pattern to match special characters
    pattern = r'[^a-zA-Z0-9\s]'  # Keep letters, numbers, and spaces

    # Use the re.sub() function to remove special characters
    cleaned_text = re.sub(pattern, '', text)

    return cleaned_text

def filter_documents_by_keywords(doc: fitz.Document, key_words):
    """
    Filters documents based on keywords.

    Args:
        docs fitz.Document:  document to be filtered.
        key_words (List[str]): The list of keywords used to filter the documents.

    Returns:
        List[Document]: A list of documents that contain at least one of the keywords.
    """
    # Convert key_words to set for faster lookup
    key_words_set = set(key_words)
    
    # Filter documents efficiently, handling different document structures
    _pages = []
    pages = doc.page_count
    for i in range(pages):
        page = doc.load_page(i)
        text = page.get_textpage().extractTEXT()
        if  any(kw in remove_special_characters().lower() in remove_special_characters(text).lower() 
                 for kw in key_words_set):
            _pages.append(i)
    return _pages

class ModelResponse(BaseModel):
    """Represents a model response."""
    document_id: str
    """The ID of the document associated with the response."""
    queries: list[str]
    """The list of queries made to the model."""
    predicted_response: dict
    """The list of responses predicted by the model."""
    time: float = 0
    """The time spent generating the response, in seconds."""
    source_documents: Optional[List[Any]] = None
    """The source documents used for the response."""
    pdf_type: str = "markdown"
    """The type of the pdf, can be 'markdown', 'text' or 'image'."""
    ocr_tokens: int = 0
    """The number of tokens used for OCR processing using LLM."""
    total_tokens: int = 0
    """The total number of tokens used across all operations."""

class ImageAnalyzerMode(Enum):
    """Enum for image analysis modes."""
    NONE = "none"
    """Text analysis mode."""
    ONLYIFNOTTEXT = "only_if_not_text"
    """Image analysis mode."""
    ALWAYS = "always"
    """Both text and image analysis mode."""

class PDFAnalyzerV3:
    """
    PDF analyzer to process documents and answer questionnaires using an AI query engine.
    
    OCR Functionality:
    -----------------
    This analyzer now supports OCR (Optical Character Recognition) for extracting text from images
    within PDF documents using Azure AI Vision Read API. When OCR is enabled:
    
    1. During document opening, all images in the PDF are processed through Azure AI Vision Read API
    2. Extracted text is stored in the page metadata for later retrieval
    3. Image documents include OCR text in their metadata when extracted
    4. OCR text can be accessed via the get_ocr_text_from_document() method
    
    OCR Configuration:
    - ocr_enabled: Set to True to enable OCR processing
    - Azure AI Vision endpoint: Configure AZURE_AI_VISION_ENDPOINT in config
    - API key: Configure AZURE_AI_VISION_KEY in config (or use Managed Identity for production)
    
    Azure AI Vision Features:
    - Supports multiple languages
    - Handwritten text recognition (English only)
    - High accuracy text extraction
    - Built-in retry logic and error handling
    - Enterprise-grade security and compliance
    
    Usage Example:
    -------------
    analyzer = PDFAnalyzerV3(
        name="my_analyzer",
        config_data=config,
        engine=query_engine,
        ocr_enabled=True  # Enable Azure AI Vision OCR
    )
    
    document = analyzer.open_document(pdf_bytes)  # OCR performed automatically
    images = analyzer.extract_images(document)    # Images include OCR metadata
    ocr_data = analyzer.get_ocr_text_from_document(document)  # Get all OCR text
    
    Performance Notes:
    -----------------
    - OCR processing adds latency to document opening
    - Each image requires an API call to Azure AI Vision service
    - Consider the number of images in your PDFs when enabling OCR
    - OCR text is cached in memory during the document session
    - Azure AI Vision has built-in rate limiting and retry logic
    """
    
    def __init__(self, name: str, config_data, engine: QueryEngine, region=None, analyzer_mode: ImageAnalyzerMode = ImageAnalyzerMode.ALWAYS, ocr_enabled = False) -> None:
        """
        Initializes the PDF analyzer.

        Args:
            name (str): Name of the analyzer.
            questionaire (Questionnaire or ClassifierParameter): Questionnaire or ClassifierParameter to be used for analysis.
            engine (QueryEngine): Query engine to be used.
            region (str, optional): Region of the service. If None, uses the engine's region.
            analyzer_mode (ImageAnalyzerMode): Mode for image analysis.
            ocr_enabled (bool): Whether to enable OCR for image text extraction.
        """
          # Verifica se config_data é já um ClassifierParameter ou precisa ser convertido
        if isinstance(config_data, ClassifierParameter):
            self.config = config_data
        else:
            self.config = ClassifierParameter(**config_data)
        self._questionaire = self.config.propositions
        self.name = name
        self.region = region if region is not None else AzureRegion.BRASIL_SOUTH
        # Verifica se é um ClassifierParameter e extrai o questionário
        self._query_engine = engine
        #self.region = engine.region if region is None else region
        self.block_key = "_blocks" 
        self.indexer_key = "_indexer" 
        self.analyzer_mode = analyzer_mode
        self.ocr_enabled = self.config.ocr_enabled if hasattr(self.config, 'ocr_enabled') else ocr_enabled
        
    
  
        

    async def _indexer(self, doc, indexer:IndexerField):
        """
        Indexa as páginas com informações sobre combustíveis e lubrificantes.

        Args:
            documents: Documentos a serem analisados.
            file: O arquivo PDF a ser processado.

        Returns:
            list: Lista de índices das páginas que contêm informações relevantes.
        """
        # Cria um questionário para identificar páginas com informações relevantes
        _indexerQuestionaire = Questionnaire({
            "indexer": Query.from_dict(indexer.indexer)
        })
        
        
        # Execute a análise com o questionário de indexação
        response = await self._execute(_indexerQuestionaire, doc)
        predicted_responses = response.predicted_response 
        indexer = []
        for i, resp in enumerate(predicted_responses['indexer']):
            if resp is not None and (resp or  str(resp).lower() == 'true'):
                indexer.append(i)
        
        # Remover duplicatas e ordenar
        indexer = sorted(list(set(indexer)))
        return indexer        

    async def _perform_ocr_with_llm(self, image_base64: str, image_format: str) -> Optional[dict]:
        """
        Performs OCR on an image using GPT (LLM) and counts the number of tokens used.
        Returns a dict with 'text' and 'token_count'.
        """
        import base64
        import io
        from PIL import Image
        import tiktoken
        import logging
        try:
            # Decode image
            image_bytes = base64.b64decode(image_base64)
            pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            # Convert to PNG bytes for GPT-4o vision
            out_buf = io.BytesIO()
            pil_img.save(out_buf, format="PNG")
            png_bytes = out_buf.getvalue()

            # Compose prompt for OCR
            prompt = "You are an OCR agent. Extract all readable text from the provided image as accurately as possible. Return only the text, no commentary."
            # Call GPT-4o vision
            response = await self._query_engine.run_query(
                    text="",
                    system_message=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": [
                        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png_bytes).decode("utf-8")}}
                    ]}
                ],
                    prev_messages=[],
                )
            
            text = response.choices[0].message.content.strip()
            # Count tokens used
            encoding = tiktoken.encoding_for_model(self._query_engine.model)
            token_count = len(encoding.encode(text))
            return {"text": text, "token_count": token_count}
        except Exception as e:
            logging.error(f"LLM OCR failed: {e}")
            return None

    def _perform_ocr(self, image_base64: str, image_format: str) -> Optional[str]:
        """
        Performs OCR on an image using Azure AI Vision Read API with retry logic.
        Ensures image dimensions are within [50, 16000] for both width and height.
        """
        import time
        from PIL import Image

        max_retries = 3
        for attempt in range(max_retries):
            try:
                from azure.ai.vision.imageanalysis import ImageAnalysisClient
                from azure.ai.vision.imageanalysis.models import VisualFeatures
                from azure.core.credentials import AzureKeyCredential
                from azure.core.exceptions import HttpResponseError

                # Initialize the Azure AI Vision client
                client = ImageAnalysisClient(
                    endpoint=config.AZURE_AI_VISION_ENDPOINT,
                    credential=AzureKeyCredential(config.AZURE_AI_VISION_KEY)
                )

                # Convert base64 to bytes and normalize dimensions
                raw_bytes = base64.b64decode(image_base64)
                pil_img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
                MIN_DIM, MAX_DIM = 200, 16000
                w, h = pil_img.size

                if min(w, h) < MIN_DIM:
                    logging.warning(f"Azure AI Vision OCR: Image too small ({w}x{h}), skipping OCR.")
                    return None

                def ensure_allowed_dimensions(img: Image.Image) -> Image.Image:
                    """Ensure image dimensions are within allowed range."""
                    w, h = img.size
                    # Downscale if a side exceeds MAX_DIM
                    if max(w, h) > MAX_DIM:
                        scale = MAX_DIM / float(max(w, h))
                        new_w = max(1, int(round(w * scale)))
                        new_h = max(1, int(round(h * scale)))
                        img = img.resize((new_w, new_h), Image.LANCZOS)
                        w, h = img.size

                    return img

                pil_img = ensure_allowed_dimensions(pil_img)

                # Re-encode to bytes for API
                fmt = (image_format or "png").lower()
                fmt_map = {"jpg": "JPEG", "jpeg": "JPEG", "png": "PNG", "bmp": "BMP", "tif": "TIFF", "tiff": "TIFF"}
                pil_fmt = fmt_map.get(fmt, "PNG")
                out_buf = io.BytesIO()
                pil_img.save(out_buf, format=pil_fmt)
                image_bytes = out_buf.getvalue()

                # Perform OCR analysis
                result = client.analyze(
                    image_data=image_bytes,
                    visual_features=[VisualFeatures.READ],
                    language="en",
                    gender_neutral_caption=True
                )

                # Extract text from the result
                extracted_text = ""
                if result.read is not None:
                    for block in result.read.blocks:
                        for text_line in block.lines:
                            extracted_text += text_line.text + "\n"

                extracted_text = extracted_text.strip()

                if extracted_text:
                    logging.info(f"Azure AI Vision OCR successfully extracted {len(extracted_text)} characters")
                    return extracted_text
                else:
                    logging.warning("Azure AI Vision OCR: No text found in image")
                    return None

            except HttpResponseError as e:
                if e.status_code == 401:
                    logging.error("Azure AI Vision OCR: Authentication failed. Check your API key and endpoint.")
                    break
                elif e.status_code == 429:
                    logging.warning("Azure AI Vision OCR: Rate limit exceeded. Retrying...")
                else:
                    logging.error(f"Azure AI Vision OCR HTTP error {e.status_code}: {e.message}")
                    break
            except ImportError as e:
                logging.error(f"Azure AI Vision SDK not installed: {e}")
                logging.info("Install with: pip install azure-ai-vision-imageanalysis")
                break
            except Exception as e:
                logging.error(f"Azure AI Vision OCR unexpected error: {str(e)}")
                break

            # Sleep before retrying
            if attempt < max_retries - 1:
                logging.info(f"Retrying OCR in 1 minute... (Attempt {attempt + 1} of {max_retries})")
                time.sleep(60)

        logging.error("Azure AI Vision OCR failed after maximum retries.")
        return None

    async def _add_ocr_to_document(self, pdf_document: fitz.Document):
        """
        Adds OCR text information to PDF document images metadata using Azure AI Vision OCR.

        Args:
            pdf_document (fitz.Document): The PDF document to process.
            
        Returns:
            int: Total number of tokens used for OCR processing.
        """
        total_ocr_tokens = 0
        try:
            for page_number in range(pdf_document.page_count):
                page = pdf_document.load_page(page_number)
                image_list = page.get_images(full=True)
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = pdf_document.extract_image(xref)
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Convert to base64 for OCR
                        base64str = base64.b64encode(image_bytes).decode("utf-8")
                        
                        # Perform OCR with Azure AI Vision
                        ocr_text = self._perform_ocr(base64str, image_ext)
                        
                        if ocr_text:
                            # Since we're not using LLM, no token count needed
                            logging.info(f"Azure OCR extracted text from page {page_number + 1}, image {img_index + 1}: {ocr_text[:100]}...")
                            
                            # Add the OCR text as text to
                            # Get the image position on the page
                            image_rect = page.get_image_rects(xref)[0] if page.get_image_rects(xref) else None
                            if image_rect:
                                # Store OCR text in page's custom attributes
                                if not hasattr(page, '_ocr_texts'):
                                    page._ocr_texts = {}
                                
                                page._ocr_texts[img_index] = ocr_text
                                
                                # Add OCR text as actual page content
                                # Use the same position as the image
                                text_insert_point = fitz.Point(image_rect.x0, image_rect.y0)  # Same position as image
                                try:
                                    # Insert text as actual page content
                                    page.insert_text(
                                        text_insert_point,  # Position at image location
                                        f"OCR Text: {ocr_text}",  # Prefix to distinguish from original content
                                        fontsize=8,  # Small font size
                                        color=(0, 0, 1)  # Blue color to distinguish from original text
                                    )
                                except Exception as e:
                                    logging.warning(f"Could not insert OCR text to page: {str(e)}")
                            
                    except Exception as e:
                        logging.error(f"Error processing image {img_index} on page {page_number}: {str(e)}")
                        continue
                        
        except Exception as e:
            logging.error(f"Error adding OCR to document: {str(e)}")
            
        # When using Azure OCR instead of LLM, no tokens are used
        return 0

    async def execute(self, file, questionaire=None):
        """
        Executa a análise do edital, indexando informações relevantes.

        Args:
            file: O arquivo PDF a ser analisado.
            filename (str): O nome do arquivo.
            questionaire (Questionnaire, optional): Questionário para análise. Se None, usa o questionário padrão.
            documents: Documentos a serem analisados. Se None, serão extraídos do arquivo.
            vector_store: O vector store a ser utilizado. Se None, um novo será criado.

        Returns:
            dict: Dicionário com os resultados da análise.
        """
        
        if questionaire is None:
            questionaire = self._questionaire
        start_time = time.time()
        document = await self.open_document(file)
        end_time = time.time()
        logging.info(f"Time to open document and OCR Documents: {end_time - start_time:.2f} seconds")
        # Generate index for pages with relevant information

        if self.config and self.config.indexers:
            for indexer in self.config.indexers:
                start_time = time.time()
                index_result = await self._indexer(document, indexer)
                end_time = time.time()
                logging.info(f"Time to indexer: {end_time - start_time:.2f} seconds")
                # Apply page filter to relevant questions
                for field in indexer.fields:
                    questionaire[field].page_filter = index_result
        
        # Call parent's _execute method with the updated questionaire
        response = await self._execute(questionaire, document, file=file)
            
        return response

    async def _execute(self, questionaire, document, file: io.BytesIO = None):
        """
        Executes PDF analysis, processing the file and returning the response.
        First attempts text extraction, and if it fails or returns incomplete results,
        falls back to image analysis.

        Args:
            questionaire (Questionnaire): Questionnaire to be used.
            document (list, optional): List of extracted documents. If None, extracts from the file.
            file (io.BytesIO, optional): The PDF file as bytes stream, used for image extraction if needed.

        Returns:
            dict: Dictionary containing the response and metadata about the PDF.
        """
        assert (document is not None or file is not None)
        
        try:
            response = None
            _has_text = self.has_text(document)
            # First attempt: Text analysis
            
            response = await self._execute_for_text(document, questionaire)
            response.pdf_type = "text" if _has_text else "image"
                    
        except Exception as e:
            # If text analysis fails completely, try image analysis
            response = await self._execute_for_imgs(document, questionaire)
            response.pdf_type = "image"
            
        return response
        
    def _is_response_incomplete(self, response):
        """
        Checks if the response is incomplete by looking for None or empty values.

        Args:
            response: The response object to check.

        Returns:
            bool: True if the response is incomplete, False otherwise.
        """
        if not hasattr(response, 'predicted_response') or not response.predicted_response:
            return True
            
        # Check if any of the responses are None or empty
        for value in response.predicted_response.values():
            if value is None or (isinstance(value, (str, list)) and not value):
                return True
        return False
        
    def _merge_responses(self, text_response, img_response):
        """
        Merges text and image analysis responses, preferring non-empty values.

        Args:
            text_response: Response from text analysis
            img_response: Response from image analysis
        """
        if hasattr(img_response, 'predicted_response') and img_response.predicted_response:
            for key, img_value in img_response.predicted_response.items():
                text_value = text_response.predicted_response.get(key)
                if text_value is None or (isinstance(text_value, (str, list)) and not text_value):
                    text_response.predicted_response[key] = img_value

    async def open_document(self, file: io.BytesIO):
        """
        Opens a PDF document from a byte stream.

        Args:
            file (io.BytesIO): The byte stream of the PDF file.

        Returns:
            fitz.Document: The opened PDF document.
        """
        file.seek(0)
        pdf_document = fitz.open(stream=file.read(), filetype="pdf")

        # Perform OCR on images if enabled
        if self.ocr_enabled:
            await self._add_ocr_to_document(pdf_document)
            # Azure OCR doesn't use tokens
            pdf_document._total_ocr_tokens = 0
        else:
            pdf_document._total_ocr_tokens = 0

        return pdf_document
    
    def has_text(self, document: fitz.Document) -> bool:
        """
        Validates if the PDF document contains text.

        Args:
            document (fitz.Document): The PDF document to check.

        Returns:
            bool: True if the document contains text, False otherwise.
        """
        if not document:
            return False

        for page_num in range(document.page_count):
            page = document.load_page(page_num)
            if page.get_text().strip():
                return True
        
        return False

    def split_pdf_to_documents(self, pdf_bytes_io: io.BytesIO):
        """
        Splits a PDF into separate documents, extracting the text.

        Args:
            pdf_bytes_io (io.BytesIO): The byte stream of the PDF.

        Returns:
            list: List of documents extracted from the PDF.
        """
        pdf_bytes_io.seek(0)
        pdf_reader = PdfReader(stream=pdf_bytes_io)
        documents = []

        for i, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            # Create and return a Document object if text exists
            if text is not None and text.strip() != '':
                metadata = dict(pdf_reader.metadata or {})
                metadata['page'] = i + 1  # 1-based page numbering
                document = Document(page_content=text, metadata=metadata)
                documents.append(document)       
        return documents
    

    def extract_images(self, pdf_document, dpi=200, pages=None):
        """
        Extracts images from a PDF.

        Args:
            pdf_bytes_io (io.BytesIO): The byte stream of the PDF.
            dpi (int, optional): Resolution of the extracted images.
            pages (list, optional): List of specific pages to be processed.

        Returns:
            list: List of image documents extracted from the PDF.
        """

        images = []
        
        from llama_index.core.schema import ImageDocument
        # Loop through each page
        for page_number in range(pdf_document.page_count):
            if pages is not None and page_number not in pages:
                continue
                
            page = pdf_document.load_page(page_number)
            image_list = page.get_images(full=True)
            
            # Loop through each image
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                base64str = base64.b64encode(image_bytes).decode("utf-8")
                
                # Create image document with metadata
                metadata = {
                    "page_number": page_number + 1,
                    "image_index": img_index,
                    "image_format": image_ext
                }
                
                # Add OCR text to metadata if available
                if hasattr(page, '_ocr_texts') and img_index in page._ocr_texts:
                    metadata["ocr_text"] = page._ocr_texts[img_index]
                
                image_doc = ImageDocument(
                    image=base64str, 
                    image_mimetype=f"image/{image_ext}",
                    metadata=metadata
                )
                images.append(image_doc)
                
        return images

    def get_ocr_text_from_document(self, pdf_document: fitz.Document) -> Dict[int, Dict[int, str]]:
        """
        Retrieves all OCR text from the document.

        Args:
            pdf_document (fitz.Document): The PDF document with OCR data.

        Returns:
            Dict[int, Dict[int, str]]: Dictionary mapping page numbers to image indices and their OCR text.
        """
        ocr_data = {}
        
        for page_number in range(pdf_document.page_count):
            page = pdf_document.load_page(page_number)
            if hasattr(page, '_ocr_texts') and page._ocr_texts:
                ocr_data[page_number] = page._ocr_texts.copy()
                
        return ocr_data


    def create_vector_store(self, documents):
        """
        Creates a vector store from documents.

        Args:
            documents (List[Document]): List of documents to be indexed.

        Returns:
            FAISS: The FAISS vector store containing the document embeddings.
        """
        return faiss.FAISS.from_documents(documents, self._query_engine.embedding)
    
    def __update_query_result(self, result, queryKey, query, time, res, index_nodes, default):
        if (type(query.page_filter) is dict or type(query.page_filter) is object):
            if res is not None and res != default: 
                if  "action" in  query.page_filter:
                    if query.page_filter["action"] == "join":
                        if result[queryKey] is not None:
                            result[queryKey].append(res)
                            result[self.block_key][queryKey].append(time)
                            result[self.indexer_key][queryKey] += index_nodes
                        else:
                            result[queryKey] = [res]
                            result[self.block_key][queryKey]=[time]
                            result[self.indexer_key][queryKey] = index_nodes
                    elif query.page_filter["action"] == "first":
                        result[queryKey] = res
                        result[self.block_key][queryKey]=time
                        result[self.indexer_key][queryKey] = index_nodes
                        time = -2
                else:
                    result[queryKey] = res
                    result[self.block_key][queryKey]=time
                    result[self.indexer_key][queryKey] = index_nodes
                    time = -2
        else:
            result[queryKey] = res
        return time
    
    async def _execute_for_subqueries(self,query:Query,answer):
        """
        Executa subconsultas com base na resposta fornecida.

        Args:
            query (Query): O objeto de consulta que contém subconsultas.
            answer (str or None): A resposta a ser usada para subconsultas.
            result (dict): O dicionário onde os resultados das subconsultas serão armazenados.

        Returns:
            None
        """
        result = {}
        if answer is None:
            for queryKey, subquery in query.subqueries.items():
                result[queryKey] = query.default_value
            return result

        
        if type(answer) is list:
            for strg in answer:
                _answer += strg + '\n'
            answer = _answer
        
        for queryKey, subquery in query.subqueries.items():
            system_prompt = (
                f"{query.system_prompt}\n\n"
                "Use only the information provided in the context to answer the question. "
                "If the information is not available, respond with 'None' or 'Information not available'."
            )
            messages = [{"role": "system", "content": system_prompt}]
            messages.append({"role": "assistant", "content": f"Question: {subquery.query}"})
            messages.append({"role": "user", "content": f"Context:\n{answer}\n"})
            try:
                response = await self._query_engine.run_query(
                    text="",
                    system_message=messages,
                    prev_messages=[],
                )
                
                # Validate response structure before accessing
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    # Extract the completion message
                    completion_text = response.choices[0].message.content
                    print(f"Response for query '{subquery.text_prompt()}': {completion_text}")
                    # Process the response based on query type
                    processed_response = await self._complete_response(queryKey, subquery, completion_text)
                    result[queryKey] = processed_response
                else:
                    logging.error(f"Invalid response structure from LLM for subquery: {type(response)}")
                    result[queryKey] = subquery.default_value
               
            except (BadRequestError, RateLimitError) as e:
                logging.error(f"Error in running query: {str(e)}")
                response_obj = {"response": "Error processing request", "processed_value": None, "source_documents": []}
                result[queryKey]=  response_obj
        return result
    
    def _steps_pages(self, doc:fitz.Document, page_filter, time):
        """
        Filtra as páginas com base no filtro fornecido e no tempo.

        Args:
            pages (list): A lista de páginas a serem filtradas.
            page_filter (Union[int, list, dict]): O filtro para determinar quais páginas retornar.
            time (int): O tempo atual usado para determinar a filtragem.

        Returns:
            list: A lista filtrada de páginas.
        """
        pages = doc.page_count
        _pages=[]
        if page_filter is not None: #filra por bocos de paginas de tamnaho do page_filter , exemplo de page_filter=1 pagina  a pagina
            if type(page_filter) is int:
                if page_filter > 0:
                    start = time*page_filter
                    end = min(pages, start+page_filter)
                    _pages = range(start, end)
                else:
                    end = pages+page_filter*time
                    start = max(0, end+page_filter)
                    _pages = range(end+page_filter,end)
            elif type(page_filter) is list  or type(page_filter) is Sequence: #retonra so as paginas com indice i pertenecente a pagefilter
                _pages = []
                if time == 0:
                    for i in page_filter:
                        _pages.append(i)
            elif type(page_filter) is dict or type(page_filter) is object:  #filra por bocos de paginas de tamnaho do page_filter[count] , exemplo de page_filter=1 pagina  a pagina, se pages nao é null tem em conta so as paginas indexadas em pages
                if 'pages'in page_filter:
                    filterpages = []
                    for i in page_filter['pages']:
                        filterpages.append(pages[i])
                elif "count" in page_filter and page_filter["count"] > 0:
                    start = time*page_filter["count"]
                    end = min(pages, start+page_filter["count"])
                    _pages = range(start,end)
                elif "count" in page_filter:
                    end = pages+page_filter["count"]*time
                    start = max(0, end-page_filter["count"])
                    _pages = range(end+page_filter["count"],end)
        elif time == 0:
            _pages = range(pages)
        return list(_pages)
    
    def __filter(self,query:Query, doc, time):
        """
        Filtra os nós com base na consulta e nos critérios de filtragem.

        Args:
            query (Query): O objeto de consulta que contém critérios de filtragem.
            nodes (list): A lista de nós a serem filtrados.
            time (int): O tempo atual usado para filtragem.

        Returns:
            list: A lista filtrada de nós.
        """
        if  not query.page_filter and not query.filter:
            return None
        if query.page_filter is not None:
            _nodes = self._steps_pages(doc, query.page_filter,time)
        elif time > 0:
            return []
        if query.filter is not None and len(query.filter) > 0:
            if _nodes == []:
                _nodes = filter_documents_by_keywords(doc,query.filter)
        return _nodes

    async def _execute_for_text(self, doc: fitz.Document, questionaire: Questionnaire):
        """
        Executes questionnaire analysis for text documents.

        Args:
            doc (fitz.Document): The PDF document to be analyzed.
            questionaire (Questionnaire): The questionnaire to be used.

        Returns:
            ModelResponse: Results of the analysis.
        """
        start_time = time.time()
        queries = []
        responses = dict()
        responses[self.block_key] = dict()
        responses[self.indexer_key] = dict()
        sources = []
        
        for key, query in questionaire.items():
            # Set initial response to default value
            responses[key] = query.default_value
            t = 0
            queries.append(query.query)
            
            # Handle any subqueries by setting their default values too
            if query.subqueries:
                for subkey, subquery in query.subqueries.items():
                    responses[subkey] = subquery.default_value
                
            while t >= 0:
                context_docs_idx = self.__filter(query, doc, t)
                if context_docs_idx == []:
                    break
                if context_docs_idx is None:
                    t = -2
                    
                try:
                    # Process the document and get response
                    completion_text = await self._process_document_query(doc, query, context_docs_idx)
                    
                    # Extract structured response from completion text
                    processed_response = await self._complete_response(key, query, completion_text)
                    if processed_response is None:
                        processed_response = query.default_value
                        
                    # Update results
                    t = self.__update_query_result(responses, key, query, t, processed_response, context_docs_idx, query.default_value)
                    t += 1
                    
                    # Process subqueries if any
                    if query.subqueries:
                        subquery_obj = await self._execute_for_subqueries(query, completion_text)
                        responses.update(subquery_obj)
                        
                except (BadRequestError, RateLimitError) as e:
                    logging.error(f"Error in running query: {str(e)}")
                    responses[key] = "Error processing request"
                    sources.append([])
        
        # Create model response
        model_response = self._create_model_response(doc, queries, responses, start_time, sources)
        return model_response

    async def _process_document_query(self, doc: fitz.Document, query, context_docs_idx):
        """Helper method to process document and generate query response."""
        # Create system prompt
        system_prompt = (
            f"{query.system_prompt}\n\n"
            "Use only the information provided in the document to answer the question. "
            "If the information is not available, respond with 'None' or 'Information not available'."
        )
        
        # Extract context text
        import pymupdf4llm as pm
        def clean_text(s: str) -> str:
            import re
            # Remove control characters (except \n and \t)
            return re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]',  '', s)
            
        # Initialize context_text
        context_text = ""
        markdown_pages = []
        plain_text_pages = []
        context_docs_idx = context_docs_idx if context_docs_idx is not None else list(range(doc.page_count))
        # First pass: identify which pages need special handling
        for page_num in context_docs_idx:  # Create a copy for safe iteration
            page = doc.load_page(page_num)
            page_text = page.get_text()
            cleaned_text = clean_text(page_text)
            
            # If too many control characters were removed, handle as plain text
            if len(page_text) - len(cleaned_text) > 10:
                plain_text_pages.append((page_num, cleaned_text))
                if page_num in context_docs_idx:
                    context_docs_idx.remove(page_num)
            else:
                markdown_pages.append(page_num)
        
        # Process markdown pages
        if markdown_pages:
            markdown_content = pm.to_markdown(doc, pages=markdown_pages, ignore_images=True)
            context_text += markdown_content
        
        # Add plain text pages
        for page_num, cleaned_text in plain_text_pages:
            context_text += f"\n\n--- Page {page_num+1} (Plain Text) ---\n\n{cleaned_text}\n\n"

       
        # Get additional page text if needed
        #self._extract_pages_text(doc, context_docs_idx)
        
        # Check token count and process accordingly
        result = await self._process_with_token_management(doc, query, system_prompt, context_text, context_docs_idx)
        
        # Track token usage in document if not already present
        if hasattr(doc, '_query_tokens'):
            doc._query_tokens += result.get('token_count', 0)
        else:
            doc._query_tokens = result.get('token_count', 0)
            
        return result.get('text', '') if isinstance(result, dict) else result

    def _extract_pages_text(self, doc, pages_idx):
        """Extract text from document pages."""
        pages_text = []
        total_size = 0
        
        for page in pages_idx if pages_idx is not None else range(doc.page_count):
            page_doc = doc.load_page(page)
            page_text = page_doc.get_text()
            pages_text.append(page_text)
            total_size += len(page_text)
            
        return pages_text, total_size

    async def _process_with_token_management(self, doc, query, system_prompt, context_text, context_docs_idx):
        """Process document with token limit management."""
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(config.CURRENT_MODEL)
            max_tokens = 128000  # Safe limit below model's maximum context window
            
            # Count tokens in context_text
            token_count = len(encoding.encode(context_text))
            
            if token_count > max_tokens:
                return await self._process_chunked_document(doc, query, system_prompt, context_docs_idx, encoding, max_tokens)
            else:
                return await self._process_single_context(query, system_prompt, context_text)
        except ImportError:
            # Fallback if tiktoken is not available
            logging.warning("tiktoken not available, proceeding with full context")
            return await self._process_single_context(query, system_prompt, context_text)

    async def _process_chunked_document(self, doc, query, system_prompt, pages_idx, encoding, max_tokens):
        """Process document in chunks due to token limit."""
        logging.info("Context exceeds token limit, splitting into chunks")
        
        # Split pages into chunks to manage token count
        page_chunks = self._split_into_token_chunks(doc, pages_idx, encoding, max_tokens)
        logging.info(f"Document split into {len(page_chunks)} chunks due to token limit")
        
        # Process each chunk separately
        all_completion_texts = []
        total_token_count = 0
        
        for i, chunk_pages in enumerate(page_chunks):
            chunk_text = self._get_chunk_text(doc, chunk_pages)
            if chunk_text.strip() == "":
                continue
            # Create messages for this chunk
            chunk_messages = [{"role": "system", "content": system_prompt}]
            chunk_messages.append({
                "role": "user", 
                "content": f"Context (part {i+1} of {len(page_chunks)}):\n{chunk_text}\n\nQuestion: {query.query}"
            })
            
            # Calculate input tokens
            input_tokens = 0
            try:
                for msg in chunk_messages:
                    input_tokens += len(encoding.encode(msg["content"]))
            except Exception:
                pass
                
            # Query the engine with this chunk
            chunk_response = await self._query_engine.run_query(
                text="",
                system_message=chunk_messages,
                prev_messages=[],
            )
            
            # Calculate output tokens
            output_tokens = 0
            chunk_content = ""
            
            # Validate response structure before accessing
            if hasattr(chunk_response, 'choices') and len(chunk_response.choices) > 0:
                chunk_content = chunk_response.choices[0].message.content
                all_completion_texts.append(chunk_content)
                try:
                    output_tokens = len(encoding.encode(chunk_content))
                except Exception:
                    pass
            else:
                logging.error(f"Invalid response structure from LLM in chunk processing: {type(chunk_response)}")
                all_completion_texts.append("")
            
            # Add to total token count
            total_token_count += (input_tokens + output_tokens)
        
        # Track token usage in document
        if hasattr(doc, '_query_tokens'):
            doc._query_tokens += total_token_count
        else:
            doc._query_tokens = total_token_count
            
        # Combine all completion texts and return with token count
        return {
            "text": " ".join(all_completion_texts),
            "token_count": total_token_count
        }

    def _split_into_token_chunks(self, doc, pages_idx, encoding, max_tokens):
        """Split document pages into chunks based on token limits."""
        page_chunks = []
        current_chunk = []
        current_tokens = 0
        
        for page in pages_idx:
            page_doc = doc.load_page(page)
            page_text = page_doc.get_text()
            page_tokens = len(encoding.encode(page_text))
            
            if current_tokens + page_tokens > max_tokens and current_chunk:
                page_chunks.append(current_chunk)
                current_chunk = [page]
                current_tokens = page_tokens
            else:
                current_chunk.append(page)
                current_tokens += page_tokens
        
        if current_chunk:
            page_chunks.append(current_chunk)
            
        return page_chunks

    def _get_chunk_text(self, doc, chunk_pages):
        """Get text from a chunk of pages."""
        chunk_text = []
        for page in chunk_pages:
            page_doc = doc.load_page(page)
            chunk_text.append(page_doc.get_text())
        
        return "\n\n".join(chunk_text)

    async def _process_single_context(self, query, system_prompt, context_text):
        """Process document as a single context."""
        if context_text.strip() == "":
            return {"text": query.default_value if hasattr(query, 'default_value') else "", "token_count": 0}
        
        messages = [{"role": "system", "content": system_prompt}]
        messages.append({
            "role": "user", 
            "content": f"Context:\n{context_text}\n\nQuestion: {query.query}"
        })
        
        # Calculate input tokens
        input_tokens = 0
        try:
            import tiktoken
            encoding = tiktoken.encoding_for_model(config.CURRENT_MODEL)
            for msg in messages:
                input_tokens += len(encoding.encode(msg["content"]))
        except ImportError:
            pass
            
        response = await self._query_engine.run_query(
            text="",
            system_message=messages,
            prev_messages=[],
        )
        
        # Calculate output tokens and total
        output_tokens = 0
        result_text = ""
        
        # Validate response structure before accessing
        if hasattr(response, 'choices') and len(response.choices) > 0:
            result_text = response.choices[0].message.content
            try:
                import tiktoken
                encoding = tiktoken.encoding_for_model(config.CURRENT_MODEL)
                output_tokens = len(encoding.encode(result_text))
            except ImportError:
                pass
            return {"text": result_text, "token_count": input_tokens + output_tokens}
        else:
            logging.error(f"Invalid response structure from LLM in _process_single_context: {type(response)}")
            return {"text": query.default_value if hasattr(query, 'default_value') else "", "token_count": input_tokens}

    def _create_model_response(self, doc, queries, responses, start_time, sources):
        """Create a ModelResponse object with results."""
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Get document ID
        doc_id = "No Document"
        if doc:
            if hasattr(doc, 'metadata'):
                doc_id = doc.metadata.get("title", "Unnamed Document")
        
        # Get query token counts if available (OCR tokens will be 0 with Azure OCR)
        query_tokens = doc._query_tokens if hasattr(doc, '_query_tokens') else 0
        
        # Create model response
        return ModelResponse(
            document_id=doc_id,
            queries=queries,
            predicted_response=responses,
            time=execution_time,
            source_documents=[doc for source in sources for doc in source],
            pdf_type="markdown",
            ocr_tokens=0,
            total_tokens=query_tokens
        )

    async def _execute_for_imgs(self,document, questionaire:Questionnaire):
        """
        Executa consultas para imagens a partir de um documento e um questionário.

        Args:
            document (Any): O documento de onde as imagens serão extraídas.
            questionaire (Questionnaire): O questionário que contém as consultas.

        Returns:
            dict: Um dicionário contendo os resultados das consultas de imagem.
        """
        from monkai_shared.agent.engines.llama_query_engine import LLamaQueryEngine

        _llm_query_engine = LLamaQueryEngine(region= self.region)
        start_time = time.time()
        result = {}
        result[self.block_key] = dict()
        result[self.indexer_key] = dict()
        queries = []
        for queryKey, query in questionaire.queries.items():
            result[queryKey] = None
            t = 0
            _prompt =  query.text_prompt()
            queries.append(query.query)
            
            while t >= 0:
                _nodes_idx = self._steps_pages(document, query.page_filter,t)
                if _nodes_idx == []:
                    break  
                else:
                    _nodes =  self.extract_images(document, pages=_nodes_idx) 
                t += 1  
                if _nodes is None or len(_nodes) == 0:
                    continue
                nAnwered = True
                while nAnwered:
                    nAnwered = False  
                    try:
                        iresp = _llm_query_engine.icomplete(_prompt,_nodes)
                        res =  await self._complete_response(queryKey,query, iresp.text) 
                        t = self.__update_query_result(result, queryKey, query, t, res, [], query.default_value)
                    except BadRequestError as e:
                        if "modify your prompt and retry" in e.message:
                            nAnwered = True
                            new_prompt = _llm_query_engine.modify_prompt(_prompt)
                            if new_prompt and hasattr(new_prompt, 'text'):
                                _prompt = new_prompt.text
                        else:
                            raise PDFWrongFromat("Formato de pdf não soportado")
                    except RateLimitError:
                        nAnwered = True
                        sleep(10)

            if result[queryKey] is None:
                result[queryKey] = query.default_value
            if query.subqueries is not None:
                subs =  await self._execute_for_subqueries(query,result[queryKey])
                result.update(subs)
        logging.info(result)  
        end_time = time.time()
        model_response = ModelResponse(
            document_id= "Images Document",
            queries=queries,
            predicted_response=result,
            time= end_time  - start_time,
            source_documents= []
        ) 
        return model_response


    def getResponseTable(self, response: ModelResponse, **parameters) -> pd.DataFrame:
        """
        Generates a response table from the model response.

        Args:
            response (ModelResponse): The model response containing queries and responses.

        Returns:
            pd.DataFrame: A DataFrame with formatted responses.
        """
        data = []
        for i in range(len(response.queries)):
            query = response.queries[i]   
            _resp = response.predicted_response[i]        
            _respTxt = _resp["response"]
            
            row = {
                "doc_name": response.document_id, 
                "pergunta": query, 
                f"resp_{self.name}": _respTxt,
                f"time_{self.name}": response.time / len(response.predicted_response),
                f"resp_{self.name}_page_labels": get_page(_resp)
            }
            
            if "processed_value" in _resp and _resp["processed_value"] is not None:
                row[f"valor_{self.name}"] = _resp["processed_value"]
                
            data.append(row)
            
        return pd.DataFrame(data)

    def _convert_to_number(self, number_str: str):
        """
        Converts a numeric string to an integer.

        Args:
            number_str (str): The string representing a number.

        Returns:
            int: The converted integer.
        """
        if number_str is None or number_str.strip() == '' or number_str.lower() == 'none':
            return 0
        # Detect format and convert to numeric standard without thousands separators
        if ',' in number_str and '.' in number_str:
            if number_str.index(',') < number_str.index('.'):
                # Format: 23,000,000.00
                number_str = number_str.replace(',', '')
            else:
                # Format: 2.300.300,00
                number_str = number_str.replace('.', '')
                number_str = number_str.replace(',', '.')  # remove decimal part
        elif ',' in number_str:
            # Only commas, consider as separators
            nums = number_str.split(',')[0] 
            if len(nums) == 2 and len(nums[-1]) != 3:
                number_str = number_str.replace(',', '.')  
            else:
                number_str = number_str.replace(',', '')
        elif '.' in number_str:
            # Only dots, consider as separators
            nums = number_str.split('.')[0] 
            if len(nums) != 2 or len(nums[-1]) != 3:
                number_str = number_str.replace('.', '')
        
        return float(number_str)

    def _extract_answer(self, text: str) -> str:
        """
        Extracts the answer from text based on common answer patterns.
        If a pattern is found, returns the text after the first occurrence.
        If no pattern is found, returns the original text.

        Args:
            text (str): The text to extract the answer from.

        Returns:
            str: The extracted answer or the original text.
        """
        if text is None:
            return None
        answer_patterns = [
            "<Answer>", "</Answer>", "Answer:", "**Answer**", "**Answer:**", 
            "<Resposta>", "</Resposta>", "Resposta:", "**Resposta**", "**Resposta:**"
        ]
        
        # Check each pattern
        for pattern in answer_patterns:
            if pattern in text:
                # Get text after the pattern
                parts = text.split(pattern, 1)
                if len(parts) == 2:
                    return parts[1].strip()
        
        # If no pattern matched, return the original text
        return text

    def _extract_data(self, query: Query, response: str, query_key=None):
        """
        Extracts data from the response based on the query type.

        Args:
            query (Query): The query to be processed.
            response (str): The response to be analyzed.
            query_key (str, optional): The query key, if needed.

        Returns:
            Any: The extracted data or None.
        """
        # Extract content after answer pattern, if present
        if response is None:
            return query.default_value
        
        response = self._extract_answer(response)
        
        if query.type == PropositionType.bool:
            if 'true' in response.lower():
                return True
            elif 'false' in response.lower():
                return False
                
        elif query.type == PropositionType.numeric:
            pattern = r'-?\d[\d|\.|\,]+'
            numbers = re.findall(pattern, response)
            if len(numbers) > 0:
                return self._convert_to_number(numbers[0])
                
        elif query.type == PropositionType.choice:
            words = query.domain_values
            pattern = '|'.join(re.escape(word.lower()) for word in words)
            choices = re.findall(pattern, response.lower())
            if len(choices) == 1:
                return choices[0]
                
        elif query.type == PropositionType.date:
            pattern = r'\d{2}/\d{2}/\d{4}'
            datas = re.findall(pattern, response)
            if datas and len(datas) > 0:
                return datas[0]
                
        elif query.type == PropositionType.string:
            answers = ["<Answer>", "</Answer>", "Answer:", "**Answer**", "**Answer:**", "<Resposta>", "</Resposta>", "Resposta:", "**Resposta**", "**Resposta:**"]
            pattern = r'|'.join(re.escape(word) for word in answers) 
            response = re.sub(pattern, '', response, count=2)
            noneAnswer = ["None", "Empty Response", "Null"]
            nonePattern = r'|'.join(re.escape(word) for word in noneAnswer) 
            if re.findall(nonePattern, response):
                return query.default_value
            return response

        return query.default_value
    
    def _select_retriever(self, query: Query, query_key=None):
        """
        Selects the appropriate retriever based on the query type.

        Args:
            query (Query): The query to be processed.
            query_key (str, optional): The query key, if needed.

        Returns:
            Optional[str]: The retriever prompt, if applicable.
        """
        if query.type == PropositionType.bool:
            return vtools.bool_tool
        elif query.type == PropositionType.numeric:
            return vtools.numeric_tool
        elif query.type == PropositionType.choice:
            return vtools.choice_tool
        elif query.type == PropositionType.date:
            return vtools.data_tool
        return None
       
    async def _complete_response(self, query_key, query: Query, response: str):
        """
        Completes the response based on the query and initial response.

        Args:
            query_key (str): The query key.
            query (Query): The query object containing query details.
            response (str): The initial response to be processed.

        Returns:
            Any: The extracted value from the response or None if no valid value.
        """
        # Extract response text if it's a dict with token counts
        if isinstance(response, dict) and 'text' in response:
            response_text = response['text']
        else:
            response_text = response
            
        val = self._extract_data(query, response_text, query_key)
        if response_text is not None and (val is None or val == query.default_value) and query.type != PropositionType.string:
            retriever = self._select_retriever(query, query_key)
            if retriever is not None:
                prompt = retriever.replace('@texto', response_text)
                try:
                    # Calculate input tokens
                    input_tokens = 0
                    try:
                        import tiktoken
                        encoding = tiktoken.encoding_for_model(config.CURRENT_MODEL)
                        input_tokens = len(encoding.encode(prompt))
                    except ImportError:
                        pass
                    
                    llm_response = await self._query_engine.run_query(
                        text=prompt,
                        prev_messages=[]
                    )
                    
                    # Calculate output tokens
                    output_tokens = 0
                    
                    # Validate response structure before accessing
                    if hasattr(llm_response, 'choices') and len(llm_response.choices) > 0:
                        # Extract the completion text
                        completion_text = llm_response.choices[0].message.content
                        try:
                            import tiktoken
                            encoding = tiktoken.encoding_for_model(config.CURRENT_MODEL)
                            output_tokens = len(encoding.encode(completion_text))
                        except ImportError:
                            pass
                            
                        val = self._extract_data(query, completion_text, query_key)
                    else:
                        logging.error(f"Invalid response structure from LLM: {type(llm_response)}")
                        val = query.default_value
                    
                    # Add token count to document
                    if hasattr(self, '_query_engine') and hasattr(self._query_engine, 'doc'):
                        doc = self._query_engine.doc
                        if hasattr(doc, '_query_tokens'):
                            doc._query_tokens += (input_tokens + output_tokens)
                        else:
                            doc._query_tokens = input_tokens + output_tokens
                except Exception as e:
                    logging.error(f"Error in retrieving data: {str(e)}")
                    val = query.default_value
        if val is None or val =='None':
            return query.default_value
        return val

    def _get_summary(self, model_response: ModelResponse) -> Dict:
        """
        Generates a summary from the model response.

        Args:
            model_response (ModelResponse): The model response to summarize.

        Returns:
            Dict: A summary of the responses.
        """
        summary = {}
        
        for i, query in enumerate(model_response.queries):
            resp = model_response.predicted_response[i]
            resp_text = resp["response"]
            processed_value = resp.get("processed_value")
            
            summary[f"Q{i+1}"] = {
                "query": query,
                "response": resp_text,
                "value": processed_value,
                "pages": get_page(resp)
            }
            
        return summary
