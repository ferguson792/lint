from lint.data import Item, Source

from typing import TypeVar
from result import Ok, Err, Result, is_err, is_ok
from datetime import datetime
import sqlite3

I = TypeVar('I')
T = TypeVar('T')

def split_by_uid_presence(elements: tuple[T, ...]) -> Result[tuple[list[T], dict[I, T]], ValueError]:
    no_uid_elements = []
    uid_elements = {}
    for element in elements:
        if element.uid is None:
            no_uid_elements.append(element)
        else:
            if element.uid in uid_elements:
                return Err(ValueError(f"Duplicate source UID: {element.uid}"))
            else:
                uid_elements[element.uid] = element
    
    return Ok((no_uid_elements, uid_elements))


class StorageManager:
    db_filename: str

    def __init__(self, db_filename):
        self.db_filename = db_filename
        self.prepare_db()

    def prepare_db(self):
        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        # TODO In the future, first check whether a table
        #   exists and conforms to the expect schema,
        #   and adjust (create or migrate, or throw an error) accordingly

        # Create meta table
        try:
            CREATE_META_TABLE = '''CREATE TABLE IF NOT EXISTS meta (
                program TEXT,
                version TEXT
            );
            '''
            cursor.execute(CREATE_META_TABLE)
        except sqlite3.OperationalError as e:
            print(e)
        
        # TODO Insert meta-information into the meta table
        
        # Create table for sources
        try:
            CREATE_SOURCE_TABLE = '''CREATE TABLE IF NOT EXISTS source (
                uid INTEGER NOT NULL PRIMARY KEY,
                uri TEXT NOT NULL,
                classification TEXT NOT NULL,
                type INTEGER NOT NULL,
                status INTEGER NOT NULL
            );
            '''
            cursor.execute(CREATE_SOURCE_TABLE)
        except sqlite3.OperationalError as e:
            print(e)
        
        # Create table for items
        try:
            CREATE_ITEM_TABLE = '''CREATE TABLE IF NOT EXISTS item (
                uid INTEGER NOT NULL PRIMARY KEY,
                link TEXT,
                guid TEXT,
                pub_date TEXT,
                raw_item TEXT NOT NULL,
                source_uid INTEGER,
                access_date INTEGER,
                classification TEXT NOT NULL,
                quarantine_status INTEGER NOT NULL,
                processing_status INTEGER NOT NULL,
                FOREIGN KEY(source_uid) REFERENCES source(uid)
            );
            '''
            cursor.execute(CREATE_ITEM_TABLE)
        except sqlite3.OperationalError as e:
            print(e)

        connection.commit()
        cursor.close()
        connection.close()
    
    def update_sources(self, sources: tuple[Source, ...]) -> Result[tuple[Source, ...], Exception]:
        """
        Updates the given sources in the database. Note: This will only
        update existing sources in the database or insert new ones from the given sources,
        and will not delete sources not present in the given sources but existing in the database.

        Returns a new set of sources with their UIDs filled in.
        """
        # TODO in the future, functions such as these should
        #  be immutable and always return the state of the underlying database

        # Preparations:
        # Extract all sources which don't have a UID and turn those which have
        # a UID into a dictionary. Report duplicate UIDs.
        split_result = split_by_uid_presence(sources)
        if is_err(split_result):
            return split_result.err_value
        
        (no_uid_sources, uid_sources) = split_result.ok_value

        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()
        
        # Update sources. Iterate over stored sources to check whether the source
        # is already stored
        # TODO In the future, conflicts here should be forwarded to the human user
        #  In general, all conflicts should be given as a list of conflicts (problems)
        #  and their description
        # For sources which are identical to sources already stored, do nothing
        FIND_ITEM = '''SELECT uid FROM source
        WHERE uri = ? AND classification = ? AND type = ? AND status = ?;
        '''
        INSERT_SOURCE = '''
        INSERT INTO source (uri, classification, type, status)
        VALUES ?, ?, ?, ?
        RETURNING uid;
        '''
        for source in no_uid_sources:
            serialized_classification = ",".join(source.classification)
            parameters = (source.uri, serialized_classification, source.type, source.status)
            # Try and find a UID for the source
            result_row = cursor.execute(FIND_ITEM, parameters)
            if not result_row or result_row.rowcount == 0:
                result_row = cursor.execute(INSERT_SOURCE, parameters)

            (inserted_uid,) = result_row
            print("UID:", inserted_uid[0])
            # Update uid
            source.uid = inserted_uid[0]

        connection.commit()
        cursor.close()
        connection.close()

        return Ok(sources)

    def synchronize_items(self, items: list[Item]) -> Result[list[Item], Exception]:
        split_result = split_by_uid_presence(items)
        if is_err(split_result):
            return split_result.err_value
        
        (no_uid_items, uid_items) = split_result.ok_value

        connection = sqlite3.connect(self.db_filename)
        cursor = connection.cursor()

        FIND_ITEM = '''SELECT uid, access_date, processing_status FROM item
        WHERE link = ? AND guid = ? AND pub_date = ? AND raw_item = ? AND source_uid = ? AND classification = ? AND quarantine_status = ?;
        '''

        INSERT_ITEM = '''
        INSERT INTO item (link, guid, pub_date, raw_item, source_uid, classification, quarantine_status, access_date, processing_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        RETURNING uid;
        '''

        # For each item, either retrieve a UID or insert it into the table
        # (analogous to update_sources(), except that we ignore the access date and processing status)
        for item in no_uid_items:
            serialized_classification = ",".join(item.classification)

            parameters_find = (item.link, item.guid, item.pub_date, item.raw_item, item.source_uid, serialized_classification, item.quarantine_status.to_int())
            # Try and find a UID for the source
            result_row = cursor.execute(FIND_ITEM, parameters_find).fetchall()
            if not result_row:
                parameters_insert = parameters_find + (item.access_date.timestamp(), item.processing_status)
                result_row = cursor.execute(INSERT_ITEM, parameters_insert)
            # if we find an element, we need to update its values accordingly with the values from the database
            # (access date and processing status)
            else:
                # Update access date and processing status
                (stored_item_values,) = result_row
                item.access_date = datetime.fromtimestamp(stored_item_values[1])
                item.processing_status = stored_item_values[2]

            (inserted_uid,) = result_row
            print("UID:", inserted_uid[0])
            # Update uid
            item.uid = inserted_uid[0]

        connection.commit()
        cursor.close()
        connection.close()

        return Ok(items)
