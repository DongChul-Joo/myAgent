import os
from tqdm import tqdm
import PyPDF2
import pandas as pd
import shutil
import olefile
import zlib
import zipfile
import struct
import base64
import io
import re
from PIL import Image
from pathlib import Path
import xml.etree.ElementTree as ET

from fastapi import File, UploadFile
from langchain.schema import Document
from langchain_community.document_loaders import TextLoader,UnstructuredWordDocumentLoader,UnstructuredPowerPointLoader,UnstructuredEPubLoader
from unstructured.partition.pdf import partition_pdf

WORKDIR_PATH = os.getcwd()

FILE_UPLOAD_PATH = WORKDIR_PATH+"/resource/upload"
FILE_UPLOAD_CONTENTS_IMAGE_PATH = WORKDIR_PATH+"/resource/upload/image"

FILE_TEMP_UPLOAD_PATH = WORKDIR_PATH+"/resource/tempupload"

APPLY_FILE_TYPE_LIST = [".pdf", ".docx", ".pptx", ".epub", ".xlsx" , ".xls" , ".hwpx", ".hwp" , ".txt"]

def getFileUploadPath():
    return FILE_UPLOAD_PATH

def getFileTempUploadPath():
    return FILE_TEMP_UPLOAD_PATH

def getFileContentsImageDirPath(fileId : str):
    return os.path.join(FILE_UPLOAD_CONTENTS_IMAGE_PATH , fileId)


def moveTempToOperate(fileId: str):
    tempPath = os.path.join(FILE_TEMP_UPLOAD_PATH, fileId)
    operatePath = os.path.join(FILE_UPLOAD_PATH, fileId)
    Path(FILE_UPLOAD_PATH).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(tempPath):
        raise FileNotFoundError(f"File not found: {fileId}")
    
    try:
        # operatePath가 이미 존재하면 삭제
        if os.path.exists(operatePath):
            if os.path.isdir(operatePath):
                shutil.rmtree(operatePath)  # 디렉토리와 그 하위 파일들 모두 삭제
            else:
                os.remove(operatePath)  # 파일 삭제

        # tempPath를 operatePath로 이동
        shutil.move(tempPath, operatePath)
    except Exception as e:
        raise OSError(f"Error moving file {tempPath} to {operatePath}: {e}")
    
def moveTempToOperateChaingeId(originalFileId: str , newFileId : str):
    tempPath = os.path.join(FILE_TEMP_UPLOAD_PATH, originalFileId)
    operatePath = os.path.join(FILE_UPLOAD_PATH, newFileId)
    Path(FILE_UPLOAD_PATH).mkdir(parents=True, exist_ok=True)
    if not os.path.exists(tempPath):
        raise FileNotFoundError(f"File not found: {originalFileId}")
    
    try:
        # operatePath가 이미 존재하면 삭제
        if os.path.exists(operatePath):
            if os.path.isdir(operatePath):
                shutil.rmtree(operatePath)  # 디렉토리와 그 하위 파일들 모두 삭제
            else:
                os.remove(operatePath)  # 파일 삭제

        # tempPath를 operatePath로 이동
        shutil.move(tempPath, operatePath)
    except Exception as e:
        raise OSError(f"Error moving file {tempPath} to {operatePath}: {e}")

def copyOperateToTemp(fileId: str):
    tempPath = os.path.join(FILE_TEMP_UPLOAD_PATH, fileId)
    operatePath = os.path.join(FILE_UPLOAD_PATH, fileId)
    if not os.path.exists(operatePath):
        raise FileNotFoundError(f"File not found: {fileId}")
    
    try:
        # tempPath가 이미 존재하면 삭제
        if os.path.exists(tempPath):
            if os.path.isdir(tempPath):
                shutil.rmtree(tempPath)  # 디렉토리와 그 하위 파일들 모두 삭제
            else:
                os.remove(tempPath)  # 파일 삭제
        # operatePath를 tempPath로 이동
        shutil.copytree(operatePath, tempPath)
    except Exception as e:
        raise OSError(f"Error moving file {operatePath} to {tempPath}: {e}")
    
def deleteToOperate(fileId: str):
    operatePath = os.path.join(FILE_UPLOAD_PATH, fileId)
    
    try:
        if os.path.exists(operatePath):
            if os.path.isdir(operatePath):
                shutil.rmtree(operatePath)  # 디렉토리와 그 하위 파일들 모두 삭제
            else:
                os.remove(operatePath)  # 파일 삭제
    except Exception as e:
        return

def deleteToTemp(fileId: str):
    tempPath = os.path.join(FILE_TEMP_UPLOAD_PATH, fileId)
    
    try:
        # tempPath가 이미 존재하면 삭제
        if os.path.exists(tempPath):
            if os.path.isdir(tempPath):
                shutil.rmtree(tempPath)  # 디렉토리와 그 하위 파일들 모두 삭제
            else:
                os.remove(tempPath)  # 파일 삭제
    except Exception as e:
        return

# 함수 호출
def readTempFileByLoader(fileId: str , fileName :str , loader : str ):
    filePath = os.path.join(os.path.join(FILE_TEMP_UPLOAD_PATH,fileId) , fileName)
    func = globals().get(loader)
    if func and callable(func):
        return func(filePath)
    else:
        raise ValueError(f"Loader {loader} is not defined")

def getFileTypeList():
    return APPLY_FILE_TYPE_LIST

async def saveFile(fileId , uploadFile : UploadFile = File(...)):
    saveIdPath = os.path.join(FILE_UPLOAD_PATH , fileId)
    savePath = os.path.join(saveIdPath , uploadFile.filename)
    Path(saveIdPath).mkdir(parents=True, exist_ok=True)
    with open(savePath, 'wb') as file:
        shutil.copyfileobj(uploadFile.file, file)
    return savePath
        
async def saveFileTemp(fileId , uploadFile : UploadFile = File(...)):
    saveTempIdPath = os.path.join(FILE_TEMP_UPLOAD_PATH , fileId)
    saveTempPath = os.path.join(saveTempIdPath,uploadFile.filename)
    Path(saveTempIdPath).mkdir(parents=True, exist_ok=True)
    with open(saveTempPath , 'wb') as file:
        shutil.copyfileobj(uploadFile.file, file)
    return saveTempPath

def readPyPDF2(filePath : str):
    result = []
    with open(filePath, "rb") as pdfFileObj:
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        for idx, page in tqdm(enumerate(pdfReader.pages), total=len(pdfReader.pages)):
            result.append(convertTextToDocument(texts=page.extract_text() , page = idx))
    return result


def readUnstructuredWordDocumentLoader(filePath : str):
    loader = UnstructuredWordDocumentLoader(filePath)
    document = loader.load()
    return document

def readUnstructuredPowerPointLoader(filePath : str):
    loader = UnstructuredPowerPointLoader(filePath)
    document = loader.load()
    return document

def readUnstructuredEPubLoader(filePath : str):
    loader = UnstructuredEPubLoader(filePath)
    document = loader.load()
    return document

def readXlsx(filePath : str):
    excel_file = pd.read_excel(filePath, engine='openpyxl', sheet_name=None)

    #여기서 로우별 시트명 로우번호 넣어주면 위치 추적 가능
    def sheet_to_string(sheet, sheet_name = None):
        result = ''
        for i in range(len(sheet.index)):
            colIdx = 0
            for j in sheet.columns:
                if colIdx==0 :
                    result+="\n|"
                result += str(sheet.loc[sheet.index[i], j]).replace('nan','') + '|'
                colIdx+=1
        return result
    rowList = []

    for sheet_name, sheet_data in excel_file.items():
        rowList.append(sheet_to_string(sheet_data, sheet_name=sheet_name))
    return "\n".join(rowList)

def readXls(filePath : str):
    excel_file = pd.read_excel(filePath, sheet_name=None)

    #여기서 로우별 시트명 로우번호 넣어주면 위치 추적 가능
    def sheet_to_string(sheet, sheet_name = None):
        result = ''
        for i in range(len(sheet.index)):
            colIdx = 0
            for j in sheet.columns:
                if colIdx==0 :
                    result+="\n|"
                result += str(sheet.loc[sheet.index[i], j]).replace('nan','') + '|'
                colIdx+=1
        return result
    rowList = []

    for sheet_name, sheet_data in excel_file.items():
        rowList.append(sheet_to_string(sheet_data, sheet_name=sheet_name))
    return "\n".join(rowList)
    
def readXlsxRowGroup(filePath : str):
    excel_file = pd.read_excel(filePath, engine='openpyxl', sheet_name=None)
    #여기서 로우별 시트명 로우번호 넣어주면 위치 추적 가능
    def sheet_to_string(sheet, sheet_name = None):
        result = []
        for index, row in sheet.iterrows():
            row_string = ""
            for column in sheet.columns:
                row_string += f"{column}: {row[column]}, "
            row_string = row_string.rstrip(", ")
            row_string += "."
            result.append(row_string)
        return result
    rowList = []
    for sheet_name, sheet_data in excel_file.items():
        rowList.extend(sheet_to_string(sheet_data, sheet_name=sheet_name))
    return rowList
    """
    excel_file = pd.read_excel(filePath, engine='openpyxl', sheet_name=None)

    #여기서 로우별 시트명 로우번호 넣어주면 위치 추적 가능
    def sheet_to_string(sheet, sheet_name = None):
        result = []
        for i in range(len(sheet.index)):
            value = ''
            for j in sheet.columns:
                if pd.notna(sheet.loc[sheet.index[i], j]):
                    value += sheet.loc[sheet.index[i], j] + ' '
            result.append(value.strip())
        return result
    rowList = []

    for sheet_name, sheet_data in excel_file.items():
        rowList.extend(sheet_to_string(sheet_data, sheet_name=sheet_name))
    return rowList
    """

def readXlsRowGroup(filePath : str):
    excel_file = pd.read_excel(filePath, sheet_name=None)

    def sheet_to_string(sheet, sheet_name = None):
        result = []
        for index, row in sheet.iterrows():
            row_string = ""
            for column in sheet.columns:
                row_string += f"{column}: {row[column]}, "
            row_string = row_string.rstrip(", ")
            row_string += "."
            result.append(row_string)
        return result
    rowList = []
    for sheet_name, sheet_data in excel_file.items():
        rowList.extend(sheet_to_string(sheet_data, sheet_name=sheet_name))
    return rowList

def readHwpx(filePath : str):
    extract_dir = "./index/temp"
    if os.path.exists(extract_dir):
        for item in os.listdir(extract_dir):
            item_path = os.path.join(extract_dir, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
    with zipfile.ZipFile(filePath, "r") as zip_file:
        zip_file.extractall(extract_dir,)
    contents_dir = os.path.join(extract_dir, 'Contents')
    if os.path.exists(contents_dir):
        content_files = [os.path.join(contents_dir, filename) for filename in os.listdir(contents_dir) if "section" in filename and filename.endswith(".xml")]
    text_list = []
    for content_xml_path in content_files:
        tree = ET.parse(content_xml_path)
        root = tree.getroot()
        def process_node(node):
            if node.text is not None:
                text_list.append(node.text)
            # 현재 노드의 모든 자식 노드에 대해 재귀적으로 호출
            for child in node:
                process_node(child)
        # XML 파일을 파싱하고 루트 노드 얻기
        # 루트 노드부터 시작하여 모든 자식 노드에 접근
        process_node(root)
    textStr = "".join(text_list)
    texts = textStr
    return texts

def readHwp(filePath : str):
    f = olefile.OleFileIO(filePath)
    dirs = f.listdir()
    if ["FileHeader"] not in dirs or \
        ["\x05HwpSummaryInformation"] not in dirs:
        raise Exception("Not valid HWP")
    header = f.openstream("FileHeader")
    header_data = header.read()
    is_compressed = (header_data[36] & 1) == 1
    nums = []
    for d in dirs:
        if d[0] == "BodyText":
            nums.append(int(d[1][len("Section"):]))
    sections = ["BodyText/Section"+ str(x) for x in sorted(nums)]
    text = ""
    for section in sections:
        bodytext = f.openstream(section)
        data = bodytext.read()
        if is_compressed:
            unpacked_data = zlib.decompress(data, -15)
        else:
            unpacked_data = data
        # 각 Section 내 text 추출    
        section_text = ""
        i = 0
        size = len(unpacked_data)
        while i < size:
            header = struct.unpack_from("<I", unpacked_data, i)[0]
            rec_type = header & 0x3ff
            rec_len = (header >> 20) & 0xfff
            if rec_type in [67]:
                rec_data = unpacked_data[i+4:i+4+rec_len]
                section_text += rec_data.decode('utf-16')
                section_text += "\n"
            i += 4 + rec_len
        text += section_text
        #Document 생성
    texts = text
    return texts

def readText(filePath : str):
    loader = TextLoader(filePath, "utf8")
    document = loader.load()
    return document

def convertTextToDocument(texts, **kwargs):
    return Document(page_content=texts, metadata=kwargs)

def encodeImageToBase64(path : str):
    # 이미지 파일을 base64 문자열로 인코딩합니다.
    with open(path, "rb") as imageFile:
        return base64.b64encode(imageFile.read()).decode("utf-8")
        
def checkBase64Format(base64String):
    """문자열이 base64로 보이는지 확인"""
    return re.match("^[A-Za-z0-9+/]+[=]{0,2}$", base64String) is not None

def checkBase64FormatImage(base64String : str):
    """
    base64 데이터가 이미지인지 시작 부분을 보고 확인
    """
    image_signatures = {
        b"\xff\xd8\xff": "jpg",
        b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a": "png",
        b"\x47\x49\x46\x38": "gif",
        b"\x52\x49\x46\x46": "webp",
    }
    try:
        header = base64.b64decode(base64String)[:8]  # 처음 8바이트를 디코드하여 가져옴
        for sig, format in image_signatures.items():
            if header.startswith(sig):
                return True
        return False
    except Exception:
        return False
    
def resizeBase64Image(base64String : str, size=(128, 128)):
    """
    Base64 문자열로 인코딩된 이미지의 크기 조정
    """
    # Base64 문자열 디코드
    img_data = base64.b64decode(base64String)
    img = Image.open(io.BytesIO(img_data))

    # 이미지 크기 조정
    resized_img = img.resize(size, Image.LANCZOS)

    # 조정된 이미지를 바이트 버퍼에 저장
    buffered = io.BytesIO()
    resized_img.save(buffered, format=img.format)

    # 조정된 이미지를 Base64로 인코딩
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def readMultiModalPDFLoader(fileId: str , fileName :str , maxPartitionSize : int , newPartitionSize : int , combinePartitionSize : int):
    """
    PDF 파일에서 이미지, 테이블, 그리고 텍스트 조각을 추출합니다.
    path: 이미지(.jpg)를 저장할 파일 경로
    fname: 파일 이름
    """
    fileDirPath = os.path.join(FILE_UPLOAD_PATH, fileId)
    fileImageDirPath = os.path.join(FILE_UPLOAD_CONTENTS_IMAGE_PATH, fileId)
    print("partition start")
    pdfPartition = partition_pdf(
        filename=os.path.join(fileDirPath,fileName),
        extract_images_in_pdf = True,  # PDF 내 이미지 추출 활성화
        infer_table_structure = True,  # 테이블 구조 추론 활성화
        chunking_strategy = "by_title",  # 제목별로 텍스트 조각화
        max_characters = maxPartitionSize,  # 최대 문자 수
        new_after_n_chars = newPartitionSize,  # 이 문자 수 이후에 새로운 조각 생성
        combine_text_under_n_chars = combinePartitionSize,  # 이 문자 수 이하의 텍스트는 결합
        image_output_dir_path=fileImageDirPath,  # 이미지 출력 디렉토리 경로
    )
    print("partition end")
    """
    PDF에서 추출된 요소를 테이블과 텍스트로 분류합니다.
    raw_pdf_elements: unstructured.documents.elements의 리스트
    """
    tableList = []  # 테이블 저장 리스트
    textList = []  # 텍스트 저장 리스트
    for partition in pdfPartition:
        if "unstructured.documents.elements.Table" in str(type(partition)):
            tableList.append(str(partition))  # 테이블 요소 추가
        elif "unstructured.documents.elements.CompositeElement" in str(type(partition)):
            textList.append(str(partition))  # 텍스트 요소 추가
    
    return textList, tableList

def getDirImageListToBase64(dirPath : str):
    imageBase64List = []
    for imgFile in sorted(os.listdir(dirPath)):
        if imgFile.endswith(".jpg"):
            imgPath = os.path.join(dirPath, imgFile)
            base64_image = encodeImageToBase64(imgPath)
            imageBase64List.append(base64_image)
    return imageBase64List