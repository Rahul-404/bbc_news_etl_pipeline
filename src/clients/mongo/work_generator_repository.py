import sys
import time
from datetime import datetime
from typing import List, Optional

from bson import ObjectId

from src.entity.config_entity import MongoDBConfig
from src.exception.base import CustomException
from src.logger.logging_setup import ensure_context_id, new_task_id

from .mongo_base import MongoBaseRepository


class WorkGeneratorRepository(MongoBaseRepository):

    def __init__(
            self,
            mongo_db_config: MongoDBConfig,
            job_id: Optional[str] = None,
            task_id: Optional[str] = None,
            context_id: Optional[str] = None,
            parent_context_id: Optional[str] = None,
        ):
        super().__init__(
            mongo_db_config,
            job_id,
            task_id,
            context_id,
            parent_context_id,
        )

    @new_task_id
    @ensure_context_id
    def get_failed_jobs(self)-> Optional[List[dict]]:
        """
        Retrives the all failed jobs from 'failed_job_colleciton'.

        Returns
        -------
        List[dict] or None
            List of dictionary of all failed jobs if exists, otherwise None.

        Raises
        ------
        CustomException
            if fetching fails.
        """
        try:
            collection = self._get_collection(self.config.MONGODB_WORK_CHECKPOINT_NAME)
            result = list(collection.find().sort("date", 1))
            self.logging.info(f"Failed Jobs: {result}")
            if result:
                # Extract only dates
                return [job["date"] for job in result]
            else:
                return None
        except Exception as e:
            self.logging.error(f"Error in get_failed_jobs: {e}")
            raise CustomException(e, sys)

    @new_task_id
    @ensure_context_id
    def get_last_checkpoint(self) -> Optional[str]:
        """
        Retrieve the most recent checkpoint document from the 'work_checkpoint' collection.

        Returns
        -------
        dict or None
            Latest checkpoint document if exists, otherwise None.

        Raises
        ------
        CustomException
            If fetching fails.
        """
        start_time = time.perf_counter()
        try:
            collection = self._get_collection(self.config.MONGODB_WORK_CHECKPOINT_NAME)
            last_doc = collection.find_one(sort=[("last_processed_date", -1)])  # Desc sort for latest

            if last_doc and "last_processed_date" in last_doc:
                self.logging.info(f"Fetched last checkpoint: {last_doc}", start_time)
                date = last_doc["last_processed_date"]
            else:
                self.logging.info("No checkpoint found. Starting fresh.", start_time)
                date = None

            return date

        except Exception as e:
            self.logging.error(f"Error fetching checkpoint: {e}", start_time)
            raise CustomException(e, sys)

    @new_task_id
    @ensure_context_id
    def update_last_checkpoint(
        self,
        last_processed_date: str
    ):
        """
        Upsert (insert or update) the work checkpoint document.

        Parameters
        ----------
        last_processed_date : datetime
            The date up to which data has been processed.

        Raises
        ------
        CustomException
            If update fails.
        """
        start_time = time.perf_counter()
        try:
            collection = self._get_collection(self.config.MONGODB_WORK_CHECKPOINT_NAME)
            update_doc = {
                "$set": {
                    "last_processed_date": last_processed_date,
                    "updated_at": datetime.utcnow(),
                }
            }
            last_doc = collection.find_one(sort=[("last_processed_date", -1)])  # Desc sort for latest
            # check if last_processed_date exists
            if last_doc and "last_processed_date" in last_doc:
                collection.update_one({"_id": last_doc["_id"]}, update_doc, upsert=True)
            else:
                collection.insert_one({"_id": ObjectId(), **update_doc["$set"]})
            self.logging.info(f"Checkpoint updated for last_processed_date={last_processed_date}", start_time)

        except Exception as e:
            self.logging.error(f"Error updating checkpoint: {e}", start_time)
            raise CustomException(e, sys)

    @new_task_id
    @ensure_context_id
    def get_all_scarped_date_wise_doc_counts(self):
        """
        Get the dates and respective document counts, ordered by date.

        Returns
        -------
        list of tuple of (datetime.date, int) or None
            List of tuples containing (date, document count).
            Returns None if no documents are found.

        Raises
        ------
        CustomException
            If query execution fails.

        Examples
        --------
        >>> counts = mongo_op.get_all_scarped_date_wise_doc_counts()
        >>> if counts:
        ...     for date, count in counts:
        ...         print(date, count)
        """
        try:
            pipeline = [
                            {
                                "$group": {
                                    "_id": {  # Extract just the date part (Y-M-D)
                                        "$dateToString": {
                                            "format": "%Y-%m-%d",
                                            "date": "$published"
                                        }
                                    },
                                    "documents": { "$push": "$$ROOT" },  # Group all documents for the same date
                                    "count": { "$sum": 1 }  # Optional: count of documents per date
                                }
                            },
                            {
                                "$sort": { "_id": 1 }  # Sort by date ascending
                            }
                        ]
            collection = self._get_collection(self.config.MONGODB_DATA_COLLECTION_NAME)
            result = list(collection.aggregate(pipeline))
            date_wise_count = None
            if result:
                # Convert _id from string to datetime.date
                date_wise_count = [
                    (group['_id'], group['count'])
                    for group in result
                ]
                self.logging.info(f"Fetched latest document: {date_wise_count}")
                return date_wise_count
            else:
                self.logging.info(f"Fetched latest document: {date_wise_count}.")
                return date_wise_count
        except Exception as e:
            self.logging.error(f"Error fetching latest date: {e}")
            raise CustomException(e, sys)
