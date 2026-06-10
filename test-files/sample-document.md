## **Sample Test Document**

This is a comprehensive test document designed to verify PDF to Markdown conversion capabilities. It includes various formatting elements such as headers, paragraphs, tables, and lists. This paragraph intentionally spans multiple lines to test how the conversion handles text that continues across line breaks within the PDF structure.

## **1. Document Structure**

## **1.1 Multi-level Headers**

This section demonstrates how different heading levels are preserved during conversion. The extraction process should maintain the hierarchical structure of the document, converting PDF text styling into appropriate markdown header levels.

## **2. Text Formatting**

This paragraph contains **bold text** , _italic text_ , and _**bold italic text**_ . The conversion process should preserve these formatting elements in the markdown output, using appropriate markdown syntax for emphasis and strong emphasis.

## **3. Lists and Enumeration**

## **3.1 Unordered List**

- First item in the unordered list

- Second item with more details about the content

- Third item demonstrating list formatting

## **3.2 Ordered List**

- 1 First numbered item

- 2 Second numbered item

- 3 Third numbered item

## **4. Tables and Data**

## **4.1 Simple Table**

|**Feature**|**Status**|**Priority**|
|---|---|---|
|Header Extraction|Implemented|High|
|Table Processing|Implemented|High|



List Formatting Implemented Medium

## **4.2 Complex Table with Multi-line Cells**

The table below contains cells with multiple lines of text. This tests the conversion's ability to handle complex table structures and merge multi-line content appropriately.

|**Component**|**Description**|**Notes**|
|---|---|---|
|PDF Parser|Extracts text and structure from PDF documents|Uses PyMuPDF4LLM for fast extraction|
|Table Processor|Cleans and formats table cell content removing HTML tags|Merges multi-line cells automatically|
|Markdown Generator|Converts extracted content to clean markdown format|Optimized for LLM consumption|



## **5. Continuous Content**

This is the second page of the test document. It demonstrates how the PDF to Markdown conversion handles content that spans multiple pages. The conversion should maintain document flow and properly handle page boundaries without losing content or introducing artifacts.

## **5.1 Code and Technical Content**

Technical documentation often includes code examples or monospace text. For example: `import pymupdf4llm` or command-line instructions like `python script.py --option value` .

## **5.2 Summary Table**

|**Test Category**|**Elements Tested**|**Expected Outcome**|
|---|---|---|
|Structure|Headers (H1, H2)|Markdown headers (#, ##)|
|Formatting|Bold, Italic|Markdown emphasis (**, *)|
|Lists|Ordered, Unordered|Markdown lists (-, 1.)|
|Tables|Simple, Complex|Markdown tables with clean cells|
|Pages|Multi-page|Continuous content flow|



## **6. Conclusion**

This sample document provides a comprehensive test case for PDF to Markdown conversion. It exercises all major features including text extraction, formatting preservation, table processing with multi-line cell cleanup, list handling, and multi-page document processing. The resulting markdown should be clean, well-structured, and optimized for consumption by large language models.

