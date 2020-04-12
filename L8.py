from os import walk
import PyPDF2
from pymongo import  MongoClient
from PIL import Image
import pytesseract
import re

client = MongoClient('mongodb://localhost:27017/')
db = client['scan_files']
unrec_coll = db['unrecognized']
jpg_coll = db['jpg']


folders = []
pdf_files ={}
jpg_files = {}
files = []

tree = walk(r'C:\Users\dm-k2\PycharmProjects\1\Lesson\homework\pircing_homework\data_for_parse\tessdata\СКД_Поверка весов')
image_folder_path = r'C:\Users\dm-k2\PycharmProjects\1\Lesson\homework\pircing_homework\data_for_parse\tessdata\images'

for folder in tree:
    for file_name in folder[2]:
        if file_name.endswith('jpg'):
            jpg_files[file_name] = f'{folder[0]}\\{file_name}'
        elif file_name.endswith('pdf'):
            pdf_files[file_name] = f'{folder[0]}\\{file_name}'


class JpgScan:

    type = 'jpg'

    def __init__(self, name_, path_, path_par=''):
        self.name = name_
        self.path = path_
        self.path_par = path_par
        self.file_to_mongo()

    def extract_number(self):

        numbers = {'recognized':[], 'unrecognized': False, 'side': ''}
        img_object = Image.open(self.path)
        pytesseract.pytesseract.tesseract_cmd = r'C:\Users\dm-k2\PycharmProjects\1\Lesson\homework\pircing_homework\data_for_parse\tesseract.exe'
        text = pytesseract.image_to_string(img_object, 'rus')
        pattern0 = 'тельство'
        pattern1 = 'заводской (серийный) номер'
        pattern2 = 'заводской номер (номера)'
        if text.lower().find(pattern0) + 1:
            numbers['side'] = 'title'
            for idx, line in enumerate(text.split('\n')):
                if line.lower().find(pattern1) + 1 or line.lower().find(pattern2) + 1:
                    text_en = pytesseract.image_to_string(img_object, 'eng')
                    number = text_en.split('\n')[idx].split(' ')[-1]
                    if re.search(r'\d+', number):
                        numbers['recognized'].append(number)
                    else: numbers['unrecognized'] = True
            if not numbers['recognized']:
                numbers['unrecognized'] = True

        return numbers

    def file_to_data(self):
        numbers = self.extract_number()
        data = {'name': self.name,
                'numbers': {'recognized': numbers['recognized'],
                            'unrecognized': numbers['unrecognized'],
                            'side': numbers['side']},
                'path': self.path,
                'parent_path': self.path_par}
        return data

    def file_to_mongo(self):
        data = self.file_to_data()
        if data['numbers']['side']:
            jpg_coll.insert_one(data)
        if data['numbers']['unrecognized']:
            unrec_coll.insert_one({'name':data['name'], 'path': data['path']})


class PdfScan:

    type = 'pdf'

    def __init__(self, name_, path_):
        self.name = name_
        self.path = path_
        self.safe_pdf_image(image_folder_path)

    def extract_pdf_image(self):
        try:
            pdf_file = PyPDF2.PdfFileReader(open(self.path, 'rb'), strict=False)
        except FileNotFoundError as e:
            print(e)
            return None
        result = []
        for page_num in range(0, pdf_file.getNumPages()):
            page = pdf_file.getPage(page_num)
            page_obj = page['/Resources']['/XObject'].getObject()

            if page_obj['/Im0'].get('/Subtype') == '/Image':
                size = (page_obj['/Im0']['/Width']), (page_obj['/Im0']['/Height'])
                data = page_obj['/Im0']._data
                mode = 'RGB' if page_obj['/Im0']['/ColorSpace'] == 'DeviceRGB' else 'P'
                decoder = page_obj['/Im0']['/Filter']
                if decoder == '/DCTDecode':
                    file_type = 'jpg'
                if decoder == '/FlateDecode':
                    file_type = 'png'
                if decoder == '/JPXecode':
                    file_type = 'jp2'
                else:
                    file_type = 'bmp'

                result_strict = {
                    'page': page_num,
                    'size': size,
                    'data': data,
                    'mode': mode,
                    'file_type': file_type
                }

                result.append(result_strict)

        return result

    def safe_pdf_image(self, path_):
        files_jpg = []
        for itm in self.extract_pdf_image():
            name_jpg = f'{file_name}_#_{itm["page"]}.{itm["file_type"]}'
            jpg_path = f'{path_}\\{name_jpg}'

            with open(jpg_path, 'wb') as image:
                image.write(itm['data'])
            file_pdf_jpg = JpgScan(name_jpg, jpg_path, self.path)
            files_jpg.append(file_pdf_jpg)
        return files_jpg


if __name__ == "__main__":

    for name, path in jpg_files.items():
        file_jpg = JpgScan(name, path)

    for name, path in pdf_files.items():
        file_pdf = PdfScan(name, path)










