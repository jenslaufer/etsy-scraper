from abc import abstractmethod
import uuid
import gridfs
import datetime
import logging


class Storage():
    def __init__(self):
        super().__init__()

    @abstractmethod
    def exists(self, identifier):
        pass

    @abstractmethod
    def get_file_content(self, identifier):
        pass

    @abstractmethod
    def save_file(self, identifier, content, encoding='utf-8',
                  content_type='text/html', doc_type="search"):
        pass

    @abstractmethod
    def find_by_criteria(self, collection_name, criteria={}):
        pass

    @abstractmethod
    def save(self, collection_name, collection_identifier, data):
        pass


class MongoStorage(Storage):
    FS_FILES = "fs.files"

    def __init__(self, db):
        self.db = db
        self.fs = gridfs.GridFS(self.db)

    def exists(self, identifier):
        files = self.db[self.FS_FILES]
        num = files.count_documents({'identifier': identifier})
        exists = (num != 0)
        logging.debug(f"{identifier} exists: {exists}")
        return exists

    def get_file_content(self, identifier):
        files = self.db[self.FS_FILES]
        logging.debug(identifier)
        filedata = files.find_one({'identifier': identifier})
        if filedata != None:
            return self.fs.get_last_version(filename=filedata['filename']).read()

    def save_file(self, identifier, content, encoding='utf-8',
                  content_type='text/html', doc_type="search"):
        filename = '{}.html'.format(str(uuid.uuid4()))
        self.fs.put(content, filename=filename,
                    encoding=encoding, contentType=content_type,
                    doc_type=doc_type, identifier=identifier)

    def find_by_criteria(self, collection_name, criteria={}):
        files_col = self.db[collection_name]
        files = list(files_col.find(criteria))
        return files

    def save(self, collection_name, data):
        collection = self.db[collection_name]
        data['last_modified_date'] = datetime.datetime.utcnow()
        collection.save(data)

    def replace(self, collection_name, collection_identifier, data):
        collection = self.db[collection_name]
        data['last_modified_date'] = datetime.datetime.utcnow()
        collection.replace_one(
            collection_identifier, data, upsert=True)
